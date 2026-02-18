import json
import numpy as np
from sklearn.cluster import DBSCAN
from collections import Counter

def haversine_distance(lat1, lon1, lat2, lon2):
    """İki koordinat arasındaki mesafeyi hesaplar (metre)"""
    R = 6371000  # Dünya yarıçapı metre cinsinden
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

def two_pass_dbscan_clustering(coordinates):
    """İki aşamalı DBSCAN clustering algoritması"""
    
    if len(coordinates) <= 1:
        return coordinates, "single_point"
    
    coordinates_np = np.array(coordinates)
    
    # AŞAMA 1: KABA TEMİZLİK (Coarse Cleaning)
    # Şehirler arası outlier'ları temizle (25 km eps)
    
    eps_coarse_km = 25.0
    eps_coarse_rad = eps_coarse_km / 6371.0
    coordinates_rad = np.radians(coordinates_np)
    
    try:
        dbscan_coarse = DBSCAN(eps=eps_coarse_rad, min_samples=2, metric='haversine')
        coarse_labels = dbscan_coarse.fit_predict(coordinates_rad)
        
        # En kalabalık kümeyi bul
        coarse_counts = Counter(coarse_labels)
        if -1 in coarse_counts:
            del coarse_counts[-1]  # Noise'ı çıkar
        
        if coarse_counts:
            # En büyük kümeyi al
            largest_coarse_label = coarse_counts.most_common(1)[0][0]
            coarse_mask = coarse_labels == largest_coarse_label
            filtered_coordinates = coordinates_np[coarse_mask]
            
            print(f"    Aşama 1: {len(coordinates)} -> {len(filtered_coordinates)} koordinat (outlier temizlendi)")
        else:
            # Hiç küme bulunamadı, tüm koordinatları kullan
            filtered_coordinates = coordinates_np
            print(f"    Aşama 1: Küme bulunamadı, tüm koordinatlar korundu")
            
    except Exception as e:
        print(f"    Aşama 1 hatası: {e}, tüm koordinatlar korundu")
        filtered_coordinates = coordinates_np
    
    # AŞAMA 2: İNCE AYAR (Fine-tuning)
    # Ana bölge içindeki en yoğun alt kümeyi bul
    
    if len(filtered_coordinates) <= 1:
        return filtered_coordinates.tolist(), "coarse_cleaning_only"
    
    best_cluster_size = 0
    best_cluster_coords = None
    best_eps = None
    
    # İnce eps değerleri
    eps_fine_values = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]  # km
    min_samples_fine = max(2, min(4, len(filtered_coordinates) // 4))
    
    for eps_km in eps_fine_values:
        eps_rad = eps_km / 6371.0
        filtered_coords_rad = np.radians(filtered_coordinates)
        
        try:
            dbscan_fine = DBSCAN(eps=eps_rad, min_samples=min_samples_fine, metric='haversine')
            fine_labels = dbscan_fine.fit_predict(filtered_coords_rad)
            
            # En kalabalık kümeyi bul
            fine_counts = Counter(fine_labels)
            if -1 in fine_counts:
                del fine_counts[-1]  # Noise'ı çıkar
            
            if fine_counts:
                largest_fine_label = fine_counts.most_common(1)[0][0]
                cluster_size = fine_counts[largest_fine_label]
                
                if cluster_size > best_cluster_size:
                    best_cluster_size = cluster_size
                    fine_mask = fine_labels == largest_fine_label
                    best_cluster_coords = filtered_coordinates[fine_mask]
                    best_eps = eps_km
                    
        except Exception:
            continue
    
    # Sonuç değerlendirmesi
    if best_cluster_coords is not None and len(best_cluster_coords) >= 2:
        print(f"    Aşama 2: En iyi küme {best_cluster_size} nokta (eps={best_eps}km)")
        return best_cluster_coords.tolist(), f"two_pass_dbscan_eps_{best_eps}km"
    
    # FALLBACK: Manuel merkez-based temizleme
    if len(filtered_coordinates) >= 3:
        # Medyan merkez
        center_lat = np.median(filtered_coordinates[:, 0])
        center_lon = np.median(filtered_coordinates[:, 1])
        
        # Merkeze uzaklıkları hesapla
        distances_to_center = []
        for coord in filtered_coordinates:
            dist = haversine_distance(center_lat, center_lon, coord[0], coord[1])
            distances_to_center.append((coord, dist))
        
        # En yakın %60'ı al
        distances_to_center.sort(key=lambda x: x[1])
        num_to_keep = max(2, int(len(filtered_coordinates) * 0.6))
        final_coords = [coord for coord, _ in distances_to_center[:num_to_keep]]
        
        print(f"    Fallback: En yakın %60 ({num_to_keep} nokta) kullanıldı")
        return final_coords, "fallback_closest_60pct"
    
    # Son fallback
    print(f"    Fallback: Tüm filtrelenmiş koordinatlar kullanıldı")
    return filtered_coordinates.tolist(), "fallback_all_filtered"

def calculate_smart_radius(coordinates):
    """Akıllı radius hesaplama"""
    if len(coordinates) <= 1:
        return 100.0  # Tek nokta için 100m
    
    # Merkez hesapla
    center_lat = np.mean([coord[0] for coord in coordinates])
    center_lon = np.mean([coord[1] for coord in coordinates])
    
    # Merkeze uzaklıkları hesapla
    distances = []
    for lat, lon in coordinates:
        dist = haversine_distance(center_lat, center_lon, lat, lon)
        distances.append(dist)
    
    # İstatistikler
    avg_distance = np.mean(distances)
    std_distance = np.std(distances)
    max_distance = np.max(distances)
    percentile_75 = np.percentile(distances, 75)
    percentile_90 = np.percentile(distances, 90)
    
    # Akıllı radius hesaplama
    if max_distance < 100:  # Çok küçük alan
        radius = max(75.0, max_distance * 1.2)
    elif max_distance < 500:  # Küçük alan
        radius = max(100.0, percentile_75)
    elif max_distance < 2000:  # Orta alan
        radius = max(150.0, percentile_90)
    else:  # Büyük alan
        # Conservative approach - %75'lik coverage
        radius = min(5000.0, max(200.0, percentile_75))
    
    return radius

def two_pass_dbscan_analysis():
    """İki aşamalı DBSCAN analizi ile cluster merkez ve radius hesaplama"""
    
    print("İki Aşamalı DBSCAN Clustering Analizi Başlıyor...")
    print("=" * 60)
    
    # Final temizlenmiş dosyayı oku
    with open('geocoding_results_final_cleaned.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = {
        "algorithm": "two_pass_dbscan",
        "summary": {
            "total_labels": 0,
            "single_address_labels": 0,
            "clustered_labels": 0,
            "avg_radius": 0,
            "min_radius": float('inf'),
            "max_radius": 0,
            "method_distribution": {}
        },
        "cluster_data": {}
    }
    
    all_radii = []
    method_counts = Counter()
    processed_count = 0
    
    for label_id, addresses in data.items():
        processed_count += 1
        if processed_count % 500 == 0:
            print(f"İşlenen: {processed_count}/10390")
        
        # Koordinatları çıkar
        coordinates = []
        for addr in addresses:
            if 'latitude' in addr and 'longitude' in addr:
                lat, lon = addr['latitude'], addr['longitude']
                if not (np.isnan(lat) or np.isnan(lon)) and -90 <= lat <= 90 and -180 <= lon <= 180:
                    coordinates.append([lat, lon])
        
        if not coordinates:
            continue
        
        print(f"\nLabel {label_id}: {len(coordinates)} koordinat")
        
        if len(coordinates) == 1:
            # Tek adres - 100m radius
            lat, lon = coordinates[0]
            radius = 100.0
            final_coords = coordinates
            method = "single_address"
            print(f"    Tek adres: {lat:.6f}, {lon:.6f}")
            
        else:
            # İki aşamalı DBSCAN uygula
            final_coords, method = two_pass_dbscan_clustering(coordinates)
            
            # Radius hesapla
            radius = calculate_smart_radius(final_coords)
        
        # Merkez hesapla
        center_lat = np.mean([coord[0] for coord in final_coords])
        center_lon = np.mean([coord[1] for coord in final_coords])
        
        # Sonuçları kaydet
        results["cluster_data"][label_id] = {
            "center_lat": center_lat,
            "center_lon": center_lon,
            "radius_meters": radius,
            "cluster_size": len(final_coords),
            "total_addresses": len(addresses),
            "cluster_method": method
        }
        
        # İstatistikleri güncelle
        if len(coordinates) == 1:
            results["summary"]["single_address_labels"] += 1
        else:
            results["summary"]["clustered_labels"] += 1
        
        all_radii.append(radius)
        method_counts[method] += 1
        
        print(f"    Final: Merkez ({center_lat:.6f}, {center_lon:.6f}), Radius: {radius:.1f}m")
    
    # Summary istatistikleri
    results["summary"]["total_labels"] = len(results["cluster_data"])
    results["summary"]["method_distribution"] = dict(method_counts)
    
    if all_radii:
        results["summary"]["avg_radius"] = np.mean(all_radii)
        results["summary"]["min_radius"] = np.min(all_radii)
        results["summary"]["max_radius"] = np.max(all_radii)
    
    # Sonuçları kaydet
    with open('two_pass_dbscan_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 60)
    print(f"İKİ AŞAMALI DBSCAN ANALİZİ TAMAMLANDI")
    print(f"=" * 60)
    print(f"Toplam label: {results['summary']['total_labels']}")
    print(f"Tek adresli: {results['summary']['single_address_labels']}")
    print(f"Çoklu adresli: {results['summary']['clustered_labels']}")
    print(f"Ortalama radius: {results['summary']['avg_radius']:.2f}m")
    print(f"Min radius: {results['summary']['min_radius']:.2f}m")
    print(f"Max radius: {results['summary']['max_radius']:.2f}m")
    
    print(f"\nYöntem Dağılımı:")
    for method, count in method_counts.most_common():
        percentage = count / len(results['cluster_data']) * 100
        print(f"  {method}: {count} adet (%{percentage:.1f})")
    
    # Radius dağılımı
    radius_ranges = {
        "100m": len([r for r in all_radii if r <= 100]),
        "100-300m": len([r for r in all_radii if 100 < r <= 300]),
        "300-1km": len([r for r in all_radii if 300 < r <= 1000]),
        "1-3km": len([r for r in all_radii if 1000 < r <= 3000]),
        "3km+": len([r for r in all_radii if r > 3000])
    }
    
    print(f"\nRadius Dağılımı:")
    for range_name, count in radius_ranges.items():
        percentage = count / len(all_radii) * 100
        print(f"  {range_name}: {count} adet (%{percentage:.1f})")

if __name__ == "__main__":
    two_pass_dbscan_analysis()

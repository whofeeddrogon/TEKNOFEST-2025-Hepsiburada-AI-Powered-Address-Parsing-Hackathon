import json
import numpy as np

def is_in_istanbul(lat, lon):
    """Koordinatın İstanbul sınırları içinde olup olmadığını kontrol eder"""
    # İstanbul'un yaklaşık coğrafi sınırları
    istanbul_bounds = {
        'lat_min': 40.8,   # Güney sınır
        'lat_max': 41.6,   # Kuzey sınır  
        'lon_min': 28.1,   # Batı sınır
        'lon_max': 29.9    # Doğu sınır
    }
    
    return (istanbul_bounds['lat_min'] <= lat <= istanbul_bounds['lat_max'] and 
            istanbul_bounds['lon_min'] <= lon <= istanbul_bounds['lon_max'])

def remove_istanbul_coordinates():
    """İstanbul koordinatlarını temizler"""
    
    print("İstanbul koordinatları temizleniyor...")
    
    # Türkiye only dosyasını oku (önceden Türkiye dışı temizlenmiş)
    with open('geocoding_results_turkey_only.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cleaned_data = {}
    total_addresses = 0
    istanbul_addresses = 0
    cleaned_addresses = 0
    labels_with_istanbul = []
    
    for label_id, addresses in data.items():
        cleaned_addresses_for_label = []
        label_has_istanbul = False
        
        for addr in addresses:
            total_addresses += 1
            
            if 'latitude' in addr and 'longitude' in addr:
                lat, lon = addr['latitude'], addr['longitude']
                
                # NaN kontrolü
                if np.isnan(lat) or np.isnan(lon):
                    continue
                
                # İstanbul kontrolü
                if is_in_istanbul(lat, lon):
                    istanbul_addresses += 1
                    label_has_istanbul = True
                    print(f"İstanbul koordinatı temizlendi - Label {label_id}: {lat:.6f}, {lon:.6f}")
                    continue
                
                # Geçerli koordinat ise ekle
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    cleaned_addresses_for_label.append(addr)
                    cleaned_addresses += 1
        
        # Label'da en az bir adres kaldıysa ekle
        if cleaned_addresses_for_label:
            cleaned_data[label_id] = cleaned_addresses_for_label
        
        if label_has_istanbul:
            labels_with_istanbul.append(label_id)
    
    # Final temizlenmiş veriyi kaydet (Türkiye + İstanbul dışı temizlenmiş)
    with open('geocoding_results_final_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== TEMİZLEME SONUÇLARI ===")
    print(f"Toplam adres sayısı: {total_addresses}")
    print(f"İstanbul'da bulunan adres sayısı: {istanbul_addresses}")
    print(f"Temizlenen adres sayısı: {cleaned_addresses}")
    print(f"Temizleme oranı: %{(istanbul_addresses/total_addresses)*100:.2f}")
    print(f"İstanbul adresi olan label sayısı: {len(labels_with_istanbul)}")
    print(f"Kalan label sayısı: {len(cleaned_data)}")
    
    if len(labels_with_istanbul) <= 20:
        print(f"İstanbul adresi olan label'lar: {labels_with_istanbul}")
    else:
        print(f"İstanbul adresi olan ilk 20 label: {labels_with_istanbul[:20]}")
    
    # Kontrol örnekleri
    print(f"\n=== KONTROL ÖRNEKLERİ ===")
    sample_labels = list(cleaned_data.keys())[:5]
    for label_id in sample_labels:
        addresses = cleaned_data[label_id]
        print(f"Label {label_id}: {len(addresses)} adres")
        if addresses:
            first_addr = addresses[0]
            if 'latitude' in first_addr and 'longitude' in first_addr:
                lat, lon = first_addr['latitude'], first_addr['longitude']
                print(f"  Örnek koordinat: {lat:.6f}, {lon:.6f}")

def check_istanbul_bounds():
    """İstanbul sınırlarını kontrol eder"""
    print("=== İSTANBUL COĞRAFİ SINIRLARI ===")
    print("Enlem (Latitude): 40.8 - 41.6")
    print("Boylam (Longitude): 28.1 - 29.9")
    print("Bu sınırlar dışındaki koordinatlar korunacak.")
    print("İstanbul içindeki koordinatlar temizlenecek.")

if __name__ == "__main__":
    check_istanbul_bounds()
    remove_istanbul_coordinates()

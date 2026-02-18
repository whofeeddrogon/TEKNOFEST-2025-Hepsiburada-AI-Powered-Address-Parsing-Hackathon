import json

# İki aşamalı DBSCAN sonuçlarını oku
with open('two_pass_dbscan_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 3km üzerindeki radius değerlerini bul
large_radius_labels = []
for label_id, info in data['cluster_data'].items():
    radius = info['radius_meters']
    if radius > 3000:
        large_radius_labels.append({
            'label': label_id,
            'radius': radius,
            'cluster_size': info['cluster_size'],
            'total_addresses': info['total_addresses'],
            'method': info['cluster_method'],
            'center': (info['center_lat'], info['center_lon'])
        })

# Radius'a göre sırala
large_radius_labels.sort(key=lambda x: x['radius'], reverse=True)

print(f'3km üzerinde radius olan label sayısı: {len(large_radius_labels)}')
print(f'En büyük 15 radius değeri:')
print('-' * 80)

for i, item in enumerate(large_radius_labels[:15]):
    label = item['label']
    radius = item['radius']
    cluster_size = item['cluster_size']
    total_addresses = item['total_addresses']
    method = item['method']
    center_lat, center_lon = item['center']
    
    print(f'{i+1:2d}. Label {label:>5}: {radius:>7.1f}m ({radius/1000:.2f}km)')
    print(f'     Cluster: {cluster_size} nokta, Total: {total_addresses} adres')
    print(f'     Method: {method}')
    print(f'     Center: ({center_lat:.6f}, {center_lon:.6f})')
    print()

# Şimdi bu label'ların orijinal koordinatlarını kontrol edelim
print('=' * 80)
print('EN BÜYÜK 3 RADIUS\'UN ORİJİNAL KOORDİNATLARI:')
print('=' * 80)

# Original data'yı oku
with open('geocoding_results_final_cleaned.json', 'r', encoding='utf-8') as f:
    original_data = json.load(f)

for i, item in enumerate(large_radius_labels[:3]):
    label = item['label']
    print(f'\\nLabel {label} - Radius: {item["radius"]:.1f}m:')
    
    if label in original_data:
        addresses = original_data[label]
        print(f'Toplam {len(addresses)} adres:')
        
        for j, addr in enumerate(addresses):
            lat = addr.get('latitude', 'N/A')
            lon = addr.get('longitude', 'N/A')
            formatted_addr = addr.get('formatted_address', 'N/A')[:50]
            print(f'  {j+1:2d}. {lat:>10.6f}, {lon:>10.6f} - {formatted_addr}...')
    else:
        print('  Orijinal data\'da bulunamadı!')

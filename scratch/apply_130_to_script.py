import re
import scratch.relaxed_130_isles as r130

isles = r130.WORLD_ISLES_130
m = {isl['name']: (isl['cx'], isl['cy']) for isl in isles}

bridge_pairs = [
    # North America
    ('Canadian Shield Ontario', 'US Midwest and Great Lakes'),
    ('US Midwest and Great Lakes', 'US East Coast and New England'),
    ('US Midwest and Great Lakes', 'US South and Gulf Coast'),
    ('US South and Gulf Coast', 'Florida Peninsula'),
    ('US Rocky Mountains and Plains', 'Texas and Southern Great Plains'),
    ('Texas and Southern Great Plains', 'Northern Mexico'),
    ('Northern Mexico', 'Southern Mexico'),
    ('Southern Mexico', 'Yucatan Peninsula'),
    ('Quebec and Labrador', 'Newfoundland and Maritimes'),
    
    # South America
    ('Colombia and Northern Andes', 'Venezuela and Orinoco'),
    ('Venezuela and Orinoco', 'Guyana Coast'),
    ('Amazon Basin Heart', 'Brazil Northeast Bulge'),
    ('Amazon Basin Heart', 'Central Brazil and Cerrado Plateau'),
    ('Central Brazil and Cerrado Plateau', 'Brazil Southeast Coast'),
    ('Bolivia and Pantanal', 'Paraguay and Gran Chaco Basin'),
    ('Paraguay and Gran Chaco Basin', 'Argentina Pampas Core'),
    ('Argentina Pampas Core', 'Uruguay and Rio de la Plata'),
    ('Argentina Pampas Core', 'Patagonia Southern Wedge'),
    
    # Europe
    ('Ireland', 'Great Britain'),
    ('Great Britain', 'Western Europe Mainland Core'),
    ('Western Europe Mainland Core', 'France and Biscay Bay'),
    ('France and Biscay Bay', 'Iberian Peninsula'),
    ('Western Europe Mainland Core', 'Central Europe Germany and Alps'),
    ('Central Europe Germany and Alps', 'Denmark and Jutland Peninsula'),
    ('Central Europe Germany and Alps', 'Danube Basin and Romania'),
    ('Central Europe Germany and Alps', 'Poland and Baltic States'),
    
    # Africa
    ('Morocco and Atlas', 'Sahara Core Northwest'),
    ('Sahara Core Northwest', 'Libya and Central Sahara'),
    ('Libya and Central Sahara', 'Egypt and Nile Delta'),
    ('Gulf of Guinea Ivory Coast', 'Nigeria and Sahel'),
    ('Nigeria and Sahel', 'Sudan and Nubia Basin'),
    ('Nigeria and Sahel', 'Congo Basin Rainforest'),
    ('Congo Basin Rainforest', 'East Africa Rift and Lakes'),
    ('Congo Basin Rainforest', 'Zambia and Zimbabwe Plateau'),
    ('Zambia and Zimbabwe Plateau', 'Mozambique Channel Coast'),
    ('Zambia and Zimbabwe Plateau', 'South Africa Cape'),
    
    # Asia
    ('European Russia Core', 'Ural Mountains and West Siberia'),
    ('Ural Mountains and West Siberia', 'Central Siberia Plateau'),
    ('Central Siberia Plateau', 'East Siberia and Yakutia'),
    ('North China Core', 'Manchuria and Amur River Basin'),
    ('North China Core', 'Korean Peninsula'),
    ('North China Core', 'East China Coast and Shanghai'),
    ('North China Core', 'South China and Yangtze'),
    ('South China and Yangtze', 'Indochina Peninsula Vietnam/Thailand'),
    ('Northern India and Himalayas', 'Bengal and Ganges Delta'),
    ('Bengal and Ganges Delta', 'Indochina Peninsula Vietnam/Thailand'),
    ('Indochina Peninsula Vietnam/Thailand', 'Malay Peninsula'),
    ('Malay Peninsula', 'Borneo Heart'),
    ('Borneo Heart', 'Sulawesi and Moluccas'),
    
    # Oceania
    ('Western Australia Outback', 'Central and South Australia'),
    ('Northern Territory Australia', 'Central and South Australia'),
    ('Central and South Australia', 'Queensland and Barrier Reef'),
    ('Central and South Australia', 'Great Australian Bight and Adelaide'),
    ('Central and South Australia', 'New South Wales and Victoria'),
    ('New Zealand North Island', 'New Zealand South Island'),
]

# Generate bridges code block
bridge_lines = ["    bridges = ["]
curr_cat = None
for a, b in bridge_pairs:
    pt1 = m[a]
    pt2 = m[b]
    bridge_lines.append(f"        ({pt1}, {pt2}),  # {a} to {b}")
bridge_lines.append("    ]")
new_bridges_code = "\n".join(bridge_lines)

# Generate WORLD_ISLES code block
isles_code = ["WORLD_ISLES = ["]
# NA: 0..26
isles_code.append("    # === NORTH AMERICA (27 Islands: Arctic, Canada, US, Florida, Baja, Mexico, Central America, Caribbean) ===")
for isl in isles[0:27]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("\n    # === SOUTH AMERICA (16 Islands: Colombia, Venezuela, Guyana, Amazon, Brazil, Andes, Argentina, Patagonia) ===")
for isl in isles[27:43]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("\n    # === ATLANTIC AND EUROPE (16 Islands: Iceland, Ireland, Great Britain, Scandinavia, Western Europe, Central Europe, Iberia, Italy, Greece, East Europe) ===")
for isl in isles[43:59]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("\n    # === AFRICA (18 Islands: Morocco, Sahara, Libya, Egypt, Senegal, Guinea Coast, Nigeria, Sudan, Horn, Congo, Rift, Angola, Cape, Madagascar) ===")
for isl in isles[59:77]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("\n    # === ASIA AND MIDDLE EAST (32 Islands: Russia, Urals, Siberia, Kamchatka, Levant, Arabia, Central Asia, Iran, India, Tibet, China, Korea, Japan, Indochina, Indonesia) ===")
for isl in isles[77:109]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("\n    # === OCEANIA (12 Islands: Papua New Guinea, Australia Outback, Queensland Reef, Central Australia, New South Wales, Tasmania, New Zealand) ===")
for isl in isles[109:121]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("\n    # === ANTARCTICA (9 Islands: Antarctic Peninsula, Weddell Sea, Polar Dome Hub, Wilkes, Ross Shelves, Marie Byrd Land) ===")
for isl in isles[121:130]:
    isles_code.append(f"    {repr(isl)},")
isles_code.append("]")
new_isles_code = "\n".join(isles_code)

target_file = "/Volumes/Samsung X5 SSD/Projektek/Site/scripts/gen_island_maps.py"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace WORLD_ISLES
isles_pattern = re.compile(r"WORLD_ISLES = \[.*?\]\n", re.DOTALL)
if not isles_pattern.search(content):
    raise RuntimeError("WORLD_ISLES pattern not found!")
content = isles_pattern.sub(new_isles_code + "\n", content, count=1)

# Replace bridges
bridges_pattern = re.compile(r"    bridges = \[.*?    \]", re.DOTALL)
if not bridges_pattern.search(content):
    raise RuntimeError("bridges pattern not found!")
content = bridges_pattern.sub(new_bridges_code, content, count=1)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated scripts/gen_island_maps.py with 130-island archipelago!")

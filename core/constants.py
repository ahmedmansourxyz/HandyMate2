SERVICE_CATEGORIES = [
    ('Electrical', 'Electrical'),
    ('Gardening', 'Gardening'),
    ('Plumbing', 'Plumbing'),
    ('Carpentry', 'Carpentry'),
    ('Painting', 'Painting'),
    ('Cleaning', 'Cleaning'),
    ('Landscaping', 'Landscaping'),
    ('Roofing', 'Roofing'),
    ('Pest Control', 'Pest Control'),
]

TASKS_BY_CATEGORY = {
    'Electrical': [
        ["install_light", "Install Light Fixture"],
        ["repair_wiring", "Repair Wiring"],
        ["replace_outlet", "Replace Outlet"],
        ["install_switch", "Install Switch"],
        ["troubleshoot_circuit", "Troubleshoot Circuit"],
    ],
    'Gardening': [
        ["mow_lawn", "Mow Lawn"],
        ["trim_hedges", "Trim Hedges"],
        ["plant_flowers", "Plant Flowers"],
        ["weed_removal", "Weed Removal"],
        ["install_irrigation", "Install Irrigation System"],
    ],
    'Plumbing': [
        ["fix_leak", "Fix Water Leak"],
        ["unclog_drain", "Unclog Drain"],
        ["install_pipe", "Install New Pipe"],
        ["replace_faucet", "Replace Faucet"],
        ["repair_toilet", "Repair Toilet"],
    ],
    'Carpentry': [
        ["assemble_furniture", "Assemble Furniture"],
        ["build_shelves", "Build Shelves"],
        ["fix_door", "Fix Door Issues"],
        ["repair_stairs", "Repair Stairs"],
        ["custom_cabinet", "Custom Cabinetry"],
    ],
    'Painting': [
        ["paint_interior", "Paint Interior Walls"],
        ["paint_exterior", "Paint Exterior Walls"],
        ["stain_wood", "Stain Wood"],
        ["remove_wallpaper", "Remove Wallpaper"],
        ["touch_up", "Touch Up Work"],
    ],
    'Cleaning': [
        ["deep_clean", "Deep Clean"],
        ["carpet_clean", "Carpet Cleaning"],
        ["window_clean", "Window Cleaning"],
        ["office_clean", "Office Cleaning"],
        ["post_construction", "Post Construction Clean"],
    ],
    'Landscaping': [
        ["design_garden", "Design Garden"],
        ["install_grass", "Install Sod/Grass"],
        ["build_patios", "Build Patio"],
        ["install_fence", "Install Fence"],
        ["maintain_landscape", "Maintain Landscape"],
    ],
    'Roofing': [
        ["repair_leak", "Repair Roof Leak"],
        ["install_shingles", "Install Shingles"],
        ["replace_tiles", "Replace Roof Tiles"],
        ["inspect_roof", "Roof Inspection"],
        ["clean_gutters", "Clean Gutters"],
    ],
    'Pest Control': [
        ["exterminator_visit", "Exterminator Visit"],
        ["rodent_control", "Rodent Control"],
        ["insect_spray", "Insect Spray"],
        ["termite_inspection", "Termite Inspection"],
        ["preventative_treatment", "Preventative Treatment"],
    ],
}

CATEGORY_IMAGES = {
    'Electrical': '/static/core/images/electrical.jpg',
    'Gardening': '/static/core/images/gardening.jpg',
    'Plumbing': '/static/core/images/plumbing.jpg',
    'Carpentry': '/static/core/images/carpentry.jpg',
    'Painting': '/static/core/images/painting.jpg',
    'Cleaning': '/static/core/images/cleaning.jpg',
    'Landscaping': '/static/core/images/landscaping.jpg',
    'Roofing': '/static/core/images/roofing.jpg',
    'Pest Control': '/static/core/images/pest_control.jpg'
}

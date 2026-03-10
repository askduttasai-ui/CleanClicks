"""Generates cleanclicks.ico — Sparky cartoon boy icon (Bold & Warm theme)."""
try:
    from PIL import Image, ImageDraw
    size = 256
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)

    # Orange circle background
    d.ellipse([4, 4, size-4, size-4], fill='#f97316')

    # Inner glow ring
    d.ellipse([12, 12, size-12, size-12], outline='#fbbf24', width=4)

    # Body (shirt)
    d.rounded_rectangle([80, 148, 176, 210], radius=16, fill='#1e40af')

    # CC text area on shirt
    d.ellipse([103, 158, 153, 200], fill='rgba(255,255,255,40)')

    # Legs
    d.rounded_rectangle([88, 200, 112, 240], radius=8, fill='#1e3a8a')
    d.rounded_rectangle([144, 200, 168, 240], radius=8, fill='#1e3a8a')

    # Shoes
    d.ellipse([80, 232, 118, 250], fill='#0f172a')
    d.ellipse([138, 232, 176, 250], fill='#0f172a')

    # Arms
    d.rounded_rectangle([46, 152, 84, 172], radius=10, fill='#f97316')
    d.rounded_rectangle([172, 152, 210, 172], radius=10, fill='#f97316')

    # Head
    d.ellipse([72, 52, 184, 156], fill='#fcd34d')

    # Hair
    d.ellipse([72, 48, 184, 100], fill='#1e293b')
    d.ellipse([68, 60, 110, 104], fill='#1e293b')
    d.ellipse([146, 60, 188, 104], fill='#1e293b')

    # Hair spikes
    d.polygon([(100,50),(110,28),(120,50)], fill='#1e293b')
    d.polygon([(118,46),(128,22),(138,46)], fill='#1e293b')
    d.polygon([(136,50),(146,28),(156,50)], fill='#1e293b')

    # Eyes (big cartoon)
    d.ellipse([90, 88, 122, 118], fill='white')
    d.ellipse([134, 88, 166, 118], fill='white')
    d.ellipse([100, 96, 116, 112], fill='#1e293b')
    d.ellipse([140, 96, 156, 112], fill='#1e293b')
    d.ellipse([104, 98, 110, 104], fill='white')
    d.ellipse([144, 98, 150, 104], fill='white')

    # Big smile
    d.arc([94, 118, 162, 152], start=0, end=180, fill='#ea580c', width=4)

    # Cheeks
    d.ellipse([76, 112, 102, 132], fill=(249,115,22,80))
    d.ellipse([154, 112, 180, 132], fill=(249,115,22,80))

    # Mop handle (bottom left, glowing yellow)
    d.line([(30,230),(90,170)], fill='#92400e', width=8)

    # Mop head glow
    d.ellipse([4, 210, 56, 252], fill='#fbbf24')
    d.ellipse([0, 206, 60, 256], fill=(251,191,36,120))

    # Stars/sparkles around mop
    for sx,sy,ss in [(62,160,12),(72,148,8),(50,152,10)]:
        d.polygon([(sx,sy-ss),(sx+3,sy-3),(sx+ss,sy),(sx+3,sy+3),(sx,sy+ss),(sx-3,sy+3),(sx-ss,sy),(sx-3,sy-3)], fill='#fbbf24')

    # Save all sizes
    sizes_list = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
    imgs = [img.resize((s,s), Image.LANCZOS) for s in [256,128,64,48,32,16]]
    imgs[0].save('cleanclicks.ico', format='ICO',
        sizes=sizes_list,
        append_images=imgs[1:])
    print('Sparky icon created successfully.')
except Exception as e:
    print(f'Icon skipped: {e}')

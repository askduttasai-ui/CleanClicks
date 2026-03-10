"""Generates installer_banner.bmp for the NSIS installer."""
try:
    from PIL import Image, ImageDraw
    W, H = 164, 314
    img = Image.new('RGB', (W, H), '#1e40af')
    d = ImageDraw.Draw(img)
    for i in range(H):
        r = int(30  + (59  - 30)  * i/H)
        g = int(64  + (130 - 64)  * i/H)
        b = int(175 + (246 - 175) * i/H)
        d.line([(0,i),(W,i)], fill=(r,g,b))
    d.ellipse([32, 40, 132, 140], fill='white')
    d.line([(60, 120), (104, 76)], fill='#3b82f6', width=8)
    d.polygon([(80,100),(104,76),(116,88),(100,112),(88,118)], fill='#3b82f6')
    d.rectangle([0, H-60, W, H], fill='#1e3a8a')
    img.save('installer_banner.bmp')
    print('Banner created.')
except Exception as e:
    print(f'Banner skipped: {e}')

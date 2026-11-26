"""Build printable A4 sheets with two landscape A5 handouts per sheet."""

from html import escape
from pathlib import Path
import subprocess

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'pdf'
EDGE = Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
PEOPLE = {'noom': 'พี่หนุ่ม', 'mek': 'เมฆ', 'ef': 'เอฟ', 'bank': 'แบงค์', 'wine': 'ไวน์'}
TRAIN = ROOT / 'source' / 'ตั๊วไปกลับ กรุงเทพ เวียงจันทร์'
HOTEL = ROOT / 'source' / 'ที่พัก'


def crop_image(source, filename, bottom_fraction, left_fraction=0, right_fraction=1):
    if not source.is_file():
        raise FileNotFoundError(source)
    image = Image.open(source)
    box = (
        round(image.width * left_fraction), 0,
        round(image.width * right_fraction), round(image.height * bottom_fraction),
    )
    path = OUT / filename
    image.crop(box).save(path, optimize=True)
    temporary.append(path)
    return path.as_uri()


def panel(title, body, label=''):
    return f'''<section class="half">
      <div class="head"><span>OFFICE OUTING · LAOS</span><strong>{escape(name)}</strong></div>
      <div class="title"><h2>{escape(title)}</h2><span>{escape(label)}</span></div>
      {body}
      <div class="foot">{escape(name)} · 26-30 พ.ย. 2569 · ตรวจต้นฉบับในโทรศัพท์ก่อนใช้</div>
    </section>'''


def plan_panel():
    qr = (ROOT / 'source' / 'ตม ขาเข้า' / f'{name}.png')
    if not qr.is_file():
        raise FileNotFoundError(qr)
    activity = (ROOT / 'source' / 'one day trip.jpg').as_uri()
    body = f'''<div class="plan-columns"><div class="plan">
      <p><b>26 พ.ย.</b> 21:25 รถไฟไทย 133 จากกรุงเทพอภิวัฒน์</p>
      <p><b>27 พ.ย.</b> ประมาณ 08:00 หนองคาย · 09:05 คำสะหวาด · ควรออกจากสถานีคำสะหวาดไม่เกิน 10:30 เพื่อไป LCR · รถไฟ 11:25-12:17 ไปวังเวียง · สะพานฟ้า กาแฟ และโรงแรม</p>
      <p><b>28 พ.ย.</b> One Day Trip ตามภาพโปรแกรม</p>
      <p><b>29 พ.ย.</b> ถึงสถานีวังเวียง LCR ก่อน 09:46 · รถไฟ 10:46-11:47 ตามแผน · เข้าคำสะหวาดเป้าหมาย 17:15-17:25 · รถไฟไทย 134 เวลา 18:25</p>
      <p><b>30 พ.ย.</b> 07:20 ถึงกรุงเทพอภิวัฒน์ตามแผน</p>
      <div class="plan-note"><b>ตรวจยืนยัน:</b> QR ระบุ FRIENDSHIP BRIDGE 1 แต่แผนเข้าที่คำสะหวาด · ใบจองที่พักสองใบระบุผู้ใหญ่ 4 และ 2 คน สำหรับคณะ 5 คน · ยึดเวลาบนตั๋วจริง</div>
    </div><aside><div class="mini-label">QR ตม. ขาเข้า</div><img class="qr" src="{qr.as_uri()}"><div class="mini-label">โปรแกรม 28 พ.ย.</div><img class="activity" src="{activity}"></aside></div>'''
    return panel('แผนเที่ยว + ตม. ขาเข้า', body, 'เวียงจันทน์ - วังเวียง')


def ticket_panel(title, source, label, kind):
    image = crop_image(source, f'_crop-{slug}-{kind}.png', 0.40)
    return panel(title, f'<div class="ticket-image"><img src="{image}"></div><div class="crop-note">แสดงส่วนตั๋วสำหรับเดินทาง · ภาพต้นฉบับเต็มอยู่ในเว็บไซต์ทริป</div>', label)


def lcr_panel():
    images = []
    for kind in ('ขาไป', 'ขากลับ'):
        source = ROOT / 'source' / f'LCR {kind}' / f'{name}.jpg'
        if not source.is_file():
            raise FileNotFoundError(source)
        image = Image.open(source)
        if image.size != (1080, 2400):
            raise ValueError((source, image.size))
        path = OUT / f'_crop-{slug}-lcr-{kind}.png'
        image.crop((65, 300, 1015, 2050)).save(path, optimize=True)
        temporary.append(path)
        images.append(path.as_uri())
    body = f'''<div class="lcr-pair"><div><h3>ขาไป · 27 พ.ย.</h3><img src="{images[0]}"></div><div><h3>ขากลับ · 29 พ.ย.</h3><img src="{images[1]}"></div></div>'''
    return panel('ตั๋ว LCR · ขาไปและขากลับ', body, 'ตรวจชื่อและที่นั่งจากตั๋ว')


def hotel_panel(number):
    source = HOTEL / f'LINE_ALBUM_ที่พักวังเวียง_261115_{number}.jpg'
    image = crop_image(source, f'_crop-{slug}-hotel-{number}.png', 0.65)
    body = f'<div class="hotel-image"><img src="{image}"></div><div class="crop-note">ข้อมูลการจองและเงื่อนไขหลัก · ภาพต้นฉบับเต็มอยู่ในเว็บไซต์ทริป</div>'
    return panel(f'เอกสารที่พัก · ใบที่ {number}', body, 'โดมอน ริเวอร์ไซด์')


STYLE = '''
@page{size:A4 portrait;margin:0}*{box-sizing:border-box}body{margin:0;font-family:Tahoma,Arial,sans-serif;color:#14281e;background:#fff}
.sheet{width:210mm;height:297mm;break-after:page;overflow:hidden}.sheet:last-child{break-after:auto}
.half{width:210mm;height:148.5mm;padding:7mm 9mm 6mm;position:relative;overflow:hidden}
.half:first-child{border-bottom:1px dashed #647c6d}.half:first-child:after{content:'✂  ตัดตามเส้นนี้';position:absolute;right:9mm;bottom:0;color:#647c6d;font-size:7pt;background:white;padding:0 2mm}
.head{display:flex;justify-content:space-between;border-bottom:1px solid #9db5a4;padding-bottom:1.5mm;font-size:7pt;color:#426457}.head strong{color:#173e2d}
.title{display:flex;justify-content:space-between;align-items:baseline;gap:3mm;margin:2.5mm 0 2mm}.title h2{font-size:12pt;color:#193f30;margin:0}.title span{font-size:7.5pt;color:#52665a}
.foot{position:absolute;bottom:3.5mm;left:9mm;right:9mm;border-top:1px solid #d2ded6;padding-top:1.3mm;font-size:6.5pt;color:#5b6e62}
.plan-columns{display:grid;grid-template-columns:123mm 62mm;gap:4mm}.plan{font-size:8pt;line-height:1.36}.plan p{margin:0 0 2.3mm;padding:1.5mm 2mm;background:#f1f6f2;border-left:2mm solid #73907c}.plan p:nth-child(2){background:#f0f5f9;border-color:#5e90b3}.plan p:nth-child(4){background:#faf6ed;border-color:#d6a761}.plan-note{margin-top:1.5mm;border:1px solid #b9ccb9;padding:2mm;font-size:7pt;line-height:1.34}
aside{border:1px solid #cfddd2;padding:1.5mm;text-align:center}.mini-label{font-size:7pt;font-weight:700;margin-bottom:1mm}.qr{display:block;width:100%;max-height:72mm;object-fit:contain}.activity{display:block;width:34mm;height:auto;max-height:39mm;margin:0 auto}
.ticket-image,.hotel-image{height:107mm;display:flex;justify-content:center;align-items:flex-start}.ticket-image img{width:170mm;max-height:105mm;object-fit:contain}.hotel-image img{width:116mm;max-height:107mm;object-fit:contain}
.crop-note{text-align:center;font-size:6.5pt;color:#596b60;margin-top:1mm}
.lcr-pair{display:flex;justify-content:center;gap:16mm}.lcr-pair>div{text-align:center;width:62mm}.lcr-pair h3{font-size:8pt;margin:0 0 1mm;color:#234c36}.lcr-pair img{display:block;width:62mm;max-height:110mm;object-fit:contain}
'''


OUT.mkdir(parents=True, exist_ok=True)
for slug, name in PEOPLE.items():
    temporary = []
    try:
        panels = [
            plan_panel(),
            ticket_panel('รถไฟไทย · ขาไป', TRAIN / f'ขาไป {name}.jpg', '26 พ.ย. · ขบวน 133', 'train-out'),
            lcr_panel(),
            ticket_panel('รถไฟไทย · ขากลับ', TRAIN / f'ขากลับ {name}.jpg', '29 พ.ย. · ขบวน 134', 'train-return'),
            hotel_panel(1), hotel_panel(2),
        ]
        sheets = ''.join(f'<div class="sheet">{panels[i]}{panels[i+1]}</div>' for i in range(0, 6, 2))
        html = OUT / f'_half-sheet-{slug}.html'
        temporary.append(html)
        html.write_text(f'<!doctype html><html lang="th"><head><meta charset="utf-8"><style>{STYLE}</style></head><body>{sheets}</body></html>', encoding='utf-8')
        pdf = OUT / f'trip-handout-a5-{slug}.pdf'
        subprocess.run([str(EDGE), '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--allow-file-access-from-files', f'--print-to-pdf={pdf}', html.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(slug, pdf.stat().st_size)
    finally:
        for path in temporary:
            path.unlink(missing_ok=True)

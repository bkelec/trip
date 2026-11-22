'use strict';
(() => {
  const panel = document.createElement('details');
  panel.className = 'pwa-panel';
  panel.innerHTML = `<summary>ติดตั้ง / ใช้ออฟไลน์<span class="pwa-status" role="status" aria-live="polite">กำลังเตรียมข้อมูลออฟไลน์…</span></summary>
    <div class="pwa-actions"><button type="button" data-install hidden>ติดตั้งลงโทรศัพท์</button><button type="button" data-save>อัปเดตข้อมูลออฟไลน์</button></div>
    <p>Android: เปิดด้วย Chrome → เมนู ⋮ → ติดตั้งแอป / เพิ่มไปยังหน้าจอหลัก</p>
    <p>iPhone: เปิดด้วย Safari → แชร์ → เพิ่มไปยังหน้าจอโฮม</p>
    <p>เปิดแอปที่ติดตั้งขณะมีอินเทอร์เน็ตครั้งแรก และรอ “พร้อมใช้ออฟไลน์” ก่อนเดินทาง รูปและเอกสารใช้พื้นที่ประมาณ 7 MB</p>
    <p>Google Maps, Facebook, TikTok และเว็บภายนอกยังต้องใช้อินเทอร์เน็ต หากเพิ่มเอกสารใหม่ให้กดอัปเดตขณะออนไลน์</p>`;
  document.querySelector('.page-menu').after(panel);
  const label = panel.querySelector('.pwa-status');
  const save = panel.querySelector('[data-save]');
  const install = panel.querySelector('[data-install]');
  let registration, prompt, status;
  const show = result => {
    status = result;
    if (result.ready) label.textContent = `พร้อมใช้ออฟไลน์ · ${result.images} รูป` + (navigator.onLine ? '' : ' · ไม่มีอินเทอร์เน็ต');
    else label.textContent = 'บันทึกยังไม่ครบ กรุณาต่ออินเทอร์เน็ตแล้วลองอัปเดตอีกครั้ง';
  };
  const message = type => new Promise((resolve, reject) => {
    const worker = registration.active;
    if (!worker) return reject(new Error('not ready'));
    const channel = new MessageChannel();
    const timer = setTimeout(() => reject(new Error('timeout')), 120000);
    channel.port1.onmessage = event => { clearTimeout(timer); channel.port1.close(); resolve(event.data); };
    worker.postMessage({type}, [channel.port2]);
  });
  save.addEventListener('click', async () => {
    if (!registration) return;
    if (!navigator.onLine) { label.textContent = 'ต่ออินเทอร์เน็ตก่อนอัปเดต · ข้อมูลที่บันทึกไว้ยังเปิดได้'; return; }
    save.disabled = true;
    label.textContent = 'กำลังบันทึกหน้าเว็บและรูปทั้งหมด…';
    try { await registration.update(); show(await message('SAVE_OFFLINE')); }
    catch (_) { label.textContent = 'อัปเดตไม่สำเร็จ ลองใหม่เมื่ออินเทอร์เน็ตพร้อม'; }
    finally { save.disabled = false; }
  });
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); prompt = event; install.hidden = false;
  });
  install.addEventListener('click', async () => {
    if (!prompt) return;
    await prompt.prompt(); await prompt.userChoice;
    prompt = null; install.hidden = true;
  });
  window.addEventListener('appinstalled', () => { prompt = null; install.hidden = true; });
  window.addEventListener('online', () => { if (status?.ready) show(status); });
  window.addEventListener('offline', () => { if (status?.ready) show(status); });
  if (!('serviceWorker' in navigator) || !['https:', 'http:'].includes(location.protocol) || !window.isSecureContext) {
    label.textContent = 'เปิดผ่านเว็บไซต์ HTTPS เช่น GitHub Pages เพื่อเตรียมใช้ออฟไลน์';
    save.hidden = true;
    return;
  }
  save.disabled = true;
  navigator.serviceWorker.register('sw.js', {updateViaCache: 'none'}).then(async reg => {
    registration = reg;
    if (!reg.active) {
      const worker = reg.installing || reg.waiting;
      if (worker) await new Promise((resolve, reject) => {
        const check = () => {
          if (worker.state === 'activated') resolve();
          else if (worker.state === 'redundant') reject(new Error('install failed'));
        };
        worker.addEventListener('statechange', check); check();
      });
    }
    registration = await navigator.serviceWorker.ready;
    show(await message('OFFLINE_STATUS'));
    save.disabled = false;
  }).catch(() => {
    label.textContent = 'เตรียมออฟไลน์ไม่สำเร็จ กรุณาตรวจอินเทอร์เน็ตแล้วโหลดหน้าใหม่';
    save.disabled = true;
  });
})();

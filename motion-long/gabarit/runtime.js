/* Le moteur du gabarit : les temps des mots, les aides de mouvement, le montage des scènes.
   On écrit les scènes dans scenes.js. Ce fichier change rarement. */
const LARGEUR = 1920, HAUTEUR = 1080;
const T = i => MOTS[i].d;
const F = i => MOTS[i].f;
const TOTAL = () => F(MOTS.length - 1) + .12;
const hasard = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

/* ── Aides de mouvement ── */
const nouv = (parent, cls, style = "", html = "") => { const e = document.createElement("div"); e.className = cls; if (style) e.style.cssText = style; e.innerHTML = html; parent.appendChild(e); return e; };
const impact = (tl, el, t, f = 1) => { tl.to(el, { scaleY: 1 - .2 * f, scaleX: 1 + .13 * f, duration: .06, ease: "power2.out" }, t); tl.to(el, { scaleY: 1, scaleX: 1, duration: .6, ease: "elastic.out(1,.4)" }, t + .06); };
const pop = (tl, el, t, o = {}) => { gsap.set(el, { autoAlpha: 0 }); tl.fromTo(el, { autoAlpha: 0, scale: o.de ?? .55, y: o.y ?? 24 }, { autoAlpha: 1, scale: 1, y: 0, duration: o.d ?? .42, ease: "back.out(2.2)", immediateRender: false }, t); };
const frappe = (tl, el, t, o = {}) => { gsap.set(el, { autoAlpha: 0 }); tl.fromTo(el, { autoAlpha: 0, scale: o.de ?? 1.7 }, { autoAlpha: 1, scale: 1, duration: o.d ?? .2, ease: "power4.in", immediateRender: false }, t - (o.d ?? .2)); };
const glisse = (tl, el, t, o = {}) => { gsap.set(el, { autoAlpha: 0 }); tl.fromTo(el, { autoAlpha: 0, x: o.x ?? -140 }, { autoAlpha: 1, x: 0, duration: o.d ?? .34, ease: "power3.out", immediateRender: false }, t); };
const secoue = (c, t, a = 16) => { c.tl.to(c.m, { y: a, duration: .05, ease: "power2.out" }, t); c.tl.to(c.m, { y: 0, duration: .55, ease: "elastic.out(1,.32)" }, t + .05); };
const anneau = (c, x, y, t, fin = 7) => { const e = nouv(c.m, "anneau", `left:${x}px;top:${y}px`); c.tl.fromTo(e, { opacity: 1, scale: 1 }, { opacity: 0, scale: fin, duration: .6, ease: "power2.out", immediateRender: false }, t); return e; };

/* ── L'interface : le curseur, le clic, le cadre, la barre ── */
const FLECHE = `<svg viewBox="0 0 40 56"><path d="M2 2 2 44 12.5 34 20.5 52 28.5 48.5 20.5 31 35 31Z"/></svg>`;
const monterCurseur = (c, x, y) => { const e = nouv(c.m, "curseur", "", FLECHE); gsap.set(e, { x, y }); return e; };
const vers = (c, cur, x, y, t, d = .6) => c.tl.to(cur, { x, y, duration: d, ease: "power2.inOut" }, t);
const clic = (c, cur, x, y, t) => { c.tl.to(cur, { scale: .8, duration: .05, ease: "power2.out" }, t - .05); c.tl.to(cur, { scale: 1, duration: .24, ease: "back.out(3)" }, t); anneau(c, x, y, t); };
const cadre = (c, x, y, l, h) => nouv(c.m, "cadre", `left:${x}px;top:${y}px;width:${l}px;height:${h}px`);
const barre = (c, el, t) => { const b = nouv(el, "barre"); gsap.set(b, { scaleX: 0 }); c.tl.to(b, { scaleX: 1, duration: .28, ease: "power3.inOut" }, t); return b; };

/* ── Le montage ── */
const debut = sc => sc.de === 0 ? 0 : T(sc.de);
const duree = sc => { const i = SCENES.indexOf(sc), s = SCENES[i + 1]; return (s ? debut(s) : TOTAL()) - debut(sc); };

function monter(sc, hote) {
  const S0 = debut(sc), dur = duree(sc);
  const ec = document.createElement("div"); ec.className = "ecran"; hote.appendChild(ec);
  ec.innerHTML = `<div class="mec"></div>`;
  const tl = gsap.timeline({ paused: true });
  const c = { sc, tl, dur, r: ec, m: ec.querySelector(".mec"), q: s => ec.querySelector(s), qa: s => [...ec.querySelectorAll(s)], t: i => T(i) - S0, f: i => F(i) - S0 };
  sc.monte(c);
  tl.set({}, {}, dur);
  return { ec, tl, dur, S0 };
}

function monterFilm(hote) {
  const film = gsap.timeline({ paused: true });
  SCENES.forEach((sc, i) => {
    const p = monter(sc, hote);
    gsap.set(p.ec, { visibility: i === 0 ? "visible" : "hidden" });
    film.add(p.tl.paused(false), p.S0);
    if (i > 0) film.set(p.ec, { visibility: "visible" }, p.S0);
    if (i < SCENES.length - 1) film.set(p.ec, { visibility: "hidden" }, p.S0 + p.dur);
  });
  film.set({}, {}, TOTAL());
  return film;
}

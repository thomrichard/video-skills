/* Les scènes du chapitre. L'exemple suit le texte de voix/voix.json :
   Trois(0) réglages(1) changent(2) tout.(3) Le(4) premier(5) est(6) ici.(7) Tu(8) cliques,(9) et(10) la(11) liste(12) s'ouvre.(13)
   À remplacer entièrement, en gardant la forme : nom, de, dit, bouge, pourquoi, monte(c). */
const SCENES = [
  {
    nom: "L'idée",
    de: 0,
    dit: "Trois réglages changent tout.",
    bouge: "Trois pastilles arrivent une à une sur la gauche. À droite, « tout » frappe et l'écran tremble.",
    pourquoi: "Le nombre se voit avant d'être compris, et le mot fort tombe sur le mot de la voix.",
    monte(c) {
      const { tl, t, m } = c;
      [0, 1, 2].forEach(i => {
        const p = nouv(m, "pastille", `left:150px;top:${300 + i * 180}px`, `${i + 1}`);
        pop(tl, p, t(0) + .08 + i * .16);
      });
      const mot = nouv(m, "mot", "left:640px;top:390px", `tout<span class="accent">.</span>`);
      frappe(tl, mot, t(3));
      secoue(c, t(3));
    },
  },
  {
    nom: "Le geste",
    de: 4,
    dit: "Le premier est ici. Tu cliques, et la liste s'ouvre.",
    bouge: "La fenêtre entre. Le curseur rejoint le bouton, un cadre le désigne, puis le clic ouvre la liste.",
    pourquoi: "Le spectateur reconnaît le geste qu'il fera lui-même. Dans une vraie vidéo, la fenêtre est une vraie capture.",
    monte(c) {
      const { tl, t, m } = c;
      const fen = nouv(m, "fenetre", "left:360px;top:130px;width:1200px;height:740px");
      glisse(tl, fen, 0, { x: 140 });
      const bouton = nouv(m, "bouton", "left:440px;top:220px", "Réglages");
      pop(tl, bouton, t(4) + .1);
      const cur = monterCurseur(c, 1300, 760);
      vers(c, cur, 560, 262, t(5), t(7) - t(5));
      const zone = cadre(c, 426, 206, 288, 120);
      pop(tl, zone, t(7));
      clic(c, cur, 560, 262, t(9));
      tl.set(zone, { autoAlpha: 0 }, t(9));
      ["Option A", "Option B", "Option C"].forEach((texte, i) => {
        const l = nouv(m, "ligne", `left:440px;top:${340 + i * 100}px`, texte);
        pop(tl, l, t(12) + i * .1, { de: .9, y: 16 });
      });
    },
  },
];

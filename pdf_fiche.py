"""
pdf_fiche.py — Fiche d'estimation immobilière · La Petite Agence
Design : une seule page A4 pleine, bandeau agence, lisible N&B
"""
from fpdf import FPDF
from datetime import date as Date
import os

_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Fonts ─────────────────────────────────────────────────────────────────────
def _find_font(name: str) -> str:
    local = os.path.join(_DIR, name)
    if os.path.exists(local):
        return local
    # Railway/Linux system fonts (installed via nixpacks.toml apt)
    system = f"/usr/share/fonts/truetype/dejavu/{name}"
    if os.path.exists(system):
        return system
    raise FileNotFoundError(f"Font not found: {name}")

_FONT_R  = _find_font("DejaVuSans.ttf")
_FONT_B  = _find_font("DejaVuSans-Bold.ttf")

# ── Palette ──────────────────────────────────────────────────────────────────
TEAL    = (31, 102, 120)
TEAL_D  = (22, 75, 89)
WHITE   = (255, 255, 255)
BLACK   = (20, 20, 20)
DGRAY   = (80, 80, 80)
LGRAY   = (175, 175, 175)
DIVIDER = (195, 215, 220)

# ── Dimensions ────────────────────────────────────────────────────────────────
W       = 210
H       = 297
ML      = 10
MR      = 10
MB      = 11
BH      = 22
INNER_W = W - ML - MR   # 190
GAP     = 5
COL     = (INNER_W - GAP) / 2   # 92.5

FS_SEC   = 8.0
FS_FIELD = 8.0
FS_SMALL = 7.5
FS_BIG   = 9.5
LH       = 5.2
LHF      = 5.0


def _s(v):
    return str(v).strip() if v else ""


class Fiche(FPDF):

    def __init__(self, type_bien="appartement"):
        super().__init__(unit="mm", format="A4")
        self.type_bien = type_bien
        self.add_font("R", "",  fname=_FONT_R)
        self.add_font("R", "B", fname=_FONT_B)
        self.set_margins(ML, BH + 4, MR)
        self.set_auto_page_break(auto=False)
        self.add_page()

    def footer(self):
        pass

    # ════════════════════════════════════════════════════════════════════════
    #  BANDEAU
    # ════════════════════════════════════════════════════════════════════════
    def _header(self, d):
        self.set_fill_color(*TEAL)
        self.rect(0, 0, W, BH, style="F")
        mascot = os.path.join(_DIR, "mascot.png")
        mascot_w = 0
        if os.path.exists(mascot):
            mascot_w = BH * (1472 / 3200)
            self.image(mascot, x=0, y=0, w=mascot_w, h=BH)
        tx = mascot_w + 4
        today = _s(d.get("date")) or Date.today().strftime("%d/%m/%Y")
        self.set_text_color(*WHITE)
        self.set_font("R", "B", 14)
        self.set_xy(tx, 3.5)
        self.cell(W - tx - ML - 52, 7, f".fiche estimation {self.type_bien.upper()}", ln=0)
        self.set_font("R", "", 7)
        self.set_xy(tx, 12.5)
        self.cell(50, 4, f"Date : {today}", ln=0)
        self.set_font("R", "B", 10)
        self.set_xy(W - MR - 50, 3.5)
        self.cell(50, 6, ".la petite agence", align="R", ln=0)
        self.set_font("R", "", 7)
        self.set_xy(W - MR - 50, 11)
        self.cell(50, 4, "IMMOBILIER", align="R")
        self.set_text_color(*BLACK)
        self.set_xy(ML, BH + 4)

    # ════════════════════════════════════════════════════════════════════════
    #  HELPERS
    # ════════════════════════════════════════════════════════════════════════
    def _sec(self, label, w=None):
        cw = w or INNER_W
        self.set_font("R", "B", FS_SEC)
        self.set_text_color(*TEAL_D)
        self.cell(cw, 5.5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*TEAL_D)
        self.line(self.get_x(), self.get_y(), self.get_x() + cw, self.get_y())
        self.ln(2)
        self.set_text_color(*BLACK)
        self.set_draw_color(*BLACK)

    def _f(self, label, value="", avail=None, lratio=0.46):
        avail = avail or INNER_W
        self.set_font("R", "", FS_FIELD)
        lw = min(self.get_string_width(label + " :") + 2, avail * lratio)
        vw = avail - lw
        self.set_text_color(*DGRAY)
        self.cell(lw, LHF, label + " :", ln=0)
        x = self.get_x(); y = self.get_y()
        self.set_draw_color(*LGRAY)
        self.line(x, y + LHF - 0.5, x + vw - 0.5, y + LHF - 0.5)
        self.set_text_color(*BLACK)
        v = _s(value)
        self.cell(vw, LHF, (" " + v) if v else "", new_x="LMARGIN", new_y="NEXT")

    def _lf(self, label, avail=None):
        """Champ vide — juste une ligne."""
        self._f(label, "", avail=avail)

    def _radio(self, options, selected=""):
        """Radio buttons avec wrap automatique si débordement colonne."""
        sel = selected.lower() if selected else ""
        col_right = self.l_margin + COL
        start_x = self.get_x()
        self.set_font("R", "", FS_FIELD)
        for opt in options:
            opt_w = 5 + self.get_string_width(opt) + 2
            if self.get_x() > start_x and self.get_x() + opt_w > col_right:
                self.ln(LHF)
                self.set_x(start_x)
            cx = self.get_x() + 2.0
            cy = self.get_y() + 2.4
            is_sel = opt.lower() == sel
            self.set_draw_color(*BLACK)
            self.ellipse(cx - 2, cy - 2, 4, 4, style="D")
            if is_sel:
                self.set_fill_color(*BLACK)
                self.ellipse(cx - 1.1, cy - 1.1, 2.2, 2.2, style="F")
                self.set_fill_color(*WHITE)
            self.set_text_color(*BLACK)
            self.cell(5, LHF, "", ln=0)
            self.cell(self.get_string_width(opt) + 2, LHF, opt, ln=0)

    def _chk(self, items, checked=None):
        """Cases à cocher avec wrap automatique si débordement colonne."""
        def n(s): return s.lower().replace("é","e").replace("è","e").replace("ê","e")
        checked_n = [n(c) for c in (checked or [])]
        col_right = self.l_margin + COL
        start_x = self.get_x()
        self.set_font("R", "", FS_FIELD)
        for item in items:
            item_w = 4.5 + self.get_string_width(item) + 2
            if self.get_x() > start_x and self.get_x() + item_w > col_right:
                self.ln(LHF)
                self.set_x(start_x)
            is_c = n(item) in checked_n
            x = self.get_x(); y = self.get_y()
            s = 3.0
            self.set_draw_color(*BLACK)
            self.rect(x, y + 0.8, s, s, style="D")
            if is_c:
                self.set_draw_color(*TEAL)
                self.line(x + 0.4, y + 2.1, x + s/2, y + s - 0.3)
                self.line(x + s/2, y + s - 0.3, x + s - 0.3, y + 0.9)
                self.set_draw_color(*BLACK)
            self.set_text_color(*BLACK)
            self.cell(s + 1.5, LHF, "", ln=0)
            self.cell(self.get_string_width(item) + 2, LHF, item, ln=0)

    def _divider(self, extra_below=2):
        self.set_draw_color(*DIVIDER)
        self.line(ML, self.get_y(), W - MR, self.get_y())
        self.ln(extra_below)
        self.set_draw_color(*BLACK)

    def _col_right(self, y):
        self.set_left_margin(ML + COL + GAP)
        self.set_xy(ML + COL + GAP, y)

    def _col_restore(self):
        self.set_left_margin(ML)

    def _inline_label(self, label, w=None):
        """Label gris inline sans saut de ligne."""
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lw = w or (self.get_string_width(label + " :") + 2)
        self.cell(lw, LHF, label + " :", ln=0)
        return lw

    def _inline_fill(self, w, value=""):
        """Zone de valeur avec ligne soussignée, sans saut de ligne."""
        x = self.get_x(); y = self.get_y()
        self.set_draw_color(*LGRAY)
        self.line(x, y + LHF - 0.5, x + w, y + LHF - 0.5)
        self.set_text_color(*BLACK)
        v = _s(value)
        self.cell(w, LHF, (" " + v) if v else "", ln=0)

    def _travaux_lines(self, text, n=9):
        chars = int(COL / 1.70)
        words = _s(text).split()
        lines_out = []
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 > chars:
                lines_out.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur: lines_out.append(cur)
        for i in range(n):
            txt = lines_out[i] if i < len(lines_out) else ""
            self.set_draw_color(*LGRAY)
            self.line(self.get_x(), self.get_y() + LH - 0.3,
                      self.get_x() + COL - 0.5, self.get_y() + LH - 0.3)
            self.set_font("R", "", FS_SMALL)
            self.set_text_color(*BLACK)
            self.cell(COL, LH, (" " + txt) if txt else "", new_x="LMARGIN", new_y="NEXT")

    # ════════════════════════════════════════════════════════════════════════
    #  BLOCS
    # ════════════════════════════════════════════════════════════════════════
    def _adresse(self, d):
        self.set_font("R", "B", FS_FIELD)
        self.set_text_color(*TEAL_D)
        self.cell(18, 5.5, "Adresse :", ln=0)
        self.set_draw_color(*TEAL_D)
        x = self.get_x()
        self.line(x, self.get_y() + 5, W - MR, self.get_y() + 5)
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*BLACK)
        self.cell(INNER_W - 18, 5.5, " " + _s(d.get("adresse")),
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    # ── VENDEUR individuel ────────────────────────────────────────────────────
    def _one_vendeur(self, v, label):
        """Bloc d'un vendeur — toujours affiché (lignes vides si pas de données)."""
        v = v or {}
        # Sous-titre
        self.set_font("R", "B", FS_SMALL)
        self.set_text_color(*DGRAY)
        self.cell(COL, LHF - 0.5, label, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)

        # Civilité (radio) + Situation maritale
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        self.cell(self.get_string_width("Civilité : ")+1, LHF, "Civilité : ", ln=0)
        self._radio(["Mr", "Mme"], selected=_s(v.get("civilite")))
        # Situation maritale sur la même ligne
        gap_w = 4
        self.cell(gap_w, LHF, "", ln=0)
        self._inline_label("Sit. maritale")
        rem = (self.l_margin + COL) - self.get_x() - 0.5
        self._inline_fill(rem, v.get("situation_maritale"))
        self.ln(LHF)

        # Nom / Prénom
        self._f("Nom / Prénom", (_s(v.get("nom"))+" "+_s(v.get("prenom"))).strip(), avail=COL)

        # Tél + Email sur une ligne
        hw = (COL - 2) / 2
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_tel = self.get_string_width("Tél : ")+1
        self.cell(lbl_tel, LHF, "Tél : ", ln=0)
        self._inline_fill(hw - lbl_tel, v.get("telephone"))
        self.cell(2, LHF, "", ln=0)
        lbl_em = self.get_string_width("Email : ")+1
        self.cell(lbl_em, LHF, "Email : ", ln=0)
        self._inline_fill((self.l_margin + COL) - self.get_x() - 0.5, v.get("email"))
        self.ln(LHF)

        # Notaire
        self._f("Notaire", v.get("notaire"), avail=COL)

    # ── BLOC VENDEURS ─────────────────────────────────────────────────────────
    def _bloc_vendeurs(self, d):
        self._sec(".informations vendeurs", w=COL)
        self._one_vendeur(d.get("vendeur1"), "Vendeur 1")
        self._one_vendeur(d.get("vendeur2"), "Vendeur 2")
        self.ln(2)
        # Contexte vente
        self.set_font("R", "B", FS_SMALL)
        self.set_text_color(*DGRAY)
        self.cell(COL, LHF - 0.5, "Contexte de la vente", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self._f("Prix souhaité vendeur", d.get("prix_vendeur"), avail=COL)
        self._f("Délai souhaité de vente", d.get("delai_vente"), avail=COL)
        # Situation occupante
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Situation occupante : ") + 1
        self.cell(lbl_w, LHF, "Situation occupante : ", ln=0)
        self._radio(["Libre", "Loué", "Occupé"],
                    selected=_s(d.get("situation_occupante")))
        self.ln(LHF)

    # ── CARACTÉRISTIQUES APPARTEMENT ─────────────────────────────────────────
    def _bloc_carac_appart(self, d):
        c = d.get("caracteristiques") or {}
        self._sec(".caractéristiques appartement", w=COL)
        self._f("Raison de l'estimation", c.get("raison_estimation"), avail=COL)
        self._f("Type de bien", c.get("type_bien_detail"), avail=COL)
        an = _s(c.get("annee_achat")); prix = _s(c.get("prix_achat")); reste = _s(c.get("reste_a_financer"))
        if an or prix:
            val = an + (" — " if an and prix else "") + prix
            if reste: val += f" (reste {reste})"
            self._f("Achat", val, avail=COL)
        else:
            self._f("Achat", "", avail=COL)
        self._f("Date constr. immeuble", c.get("date_construction_immeuble"), avail=COL)
        self._f("Syndic", c.get("syndic"), avail=COL)
        ch = _s(c.get("charges_copro")); comp = _s(c.get("charges_comprenant"))
        self._f("Charges copro",
                (f"{ch} EUR/mois" if ch else "") + (f"  ({comp})" if comp else ""),
                avail=COL)
        self._f("Taxe foncière", (_s(c.get("taxe_fonciere"))+" EUR") if c.get("taxe_fonciere") else "", avail=COL)

        # Chauffage
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Chauffage : ")+1
        self.cell(lbl_w, LHF, "Chauffage : ", ln=0)
        fw = 22
        self._inline_fill(fw, c.get("chauffage"))
        self.cell(3, LHF, "", ln=0)
        cht = _s(c.get("chauffage_type")).lower()
        self._radio(["Coll.", "Indiv."],
                    selected="Coll." if "coll" in cht else "Indiv." if "indiv" in cht else "")
        self.ln(LHF)

        # Ascenseur / Étage / Exposition sur une ligne
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_asc = self.get_string_width("Ascenseur : ")+1
        self.cell(lbl_asc, LHF, "Ascenseur : ", ln=0)
        asc = c.get("ascenseur")
        self._radio(["Oui", "Non"],
                    selected="Oui" if asc is True else "Non" if asc is False else "")
        self.cell(3, LHF, "", ln=0)
        self._inline_label("Étage")
        self._inline_fill(12, c.get("etage"))
        self.cell(2, LHF, "", ln=0)
        self._inline_label("Expo")
        self._inline_fill((self.l_margin + COL) - self.get_x() - 0.5, c.get("exposition"))
        self.ln(LHF)

        self._f("Huisseries / matériaux", c.get("huisseries"), avail=COL)

        # Agréments (checkbox avec wrap auto)
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Agréments : ")+1
        self.cell(lbl_w, LHF, "Agréments : ", ln=0)
        self._chk(["Balcon", "Terrasse", "Loggia", "Cave", "Grenier", "Garage", "Parking"],
                  checked=c.get("agrements") or [])
        self.ln(LHF)

        # DPE / GES
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        self.cell(self.get_string_width("DPE : ")+1, LHF, "DPE : ", ln=0)
        self._inline_fill(8, c.get("dpe"))
        self.cell(2, LHF, "", ln=0)
        self.cell(self.get_string_width("GES : ")+1, LHF, "GES : ", ln=0)
        self._inline_fill(8, c.get("ges"))
        self.cell(2, LHF, "", ln=0)
        self._inline_label("Réal. le")
        self._inline_fill((self.l_margin + COL) - self.get_x() - 0.5, c.get("dpe_date"))
        self.ln(LHF)

        # Diagnostics
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Diagnostics : ")+1
        self.cell(lbl_w, LHF, "Diagnostics : ", ln=0)
        self._chk(["Elec.", "Plomb", "Gaz", "Carrez", "Amiante"],
                  checked=c.get("diagnostics") or [])
        self.ln(LHF)

        self._f("Vis-à-vis / nuisances", c.get("vis_a_vis"), avail=COL)
        self._f("Règl. copro / points d'att.", c.get("reglement_copro"), avail=COL)

    # ── CARACTÉRISTIQUES MAISON ───────────────────────────────────────────────
    def _bloc_carac_maison(self, d):
        c = d.get("caracteristiques") or {}
        self._sec(".caractéristiques maison", w=COL)
        self._f("Raison de l'estimation", c.get("raison_estimation"), avail=COL)
        self._f("Type de bien", c.get("type_bien_detail"), avail=COL)
        an = _s(c.get("annee_achat")); prix = _s(c.get("prix_achat")); reste = _s(c.get("reste_a_financer"))
        if an or prix:
            val = an + (" — " if an and prix else "") + prix
            if reste: val += f" (reste {reste})"
            self._f("Achat", val, avail=COL)
        else:
            self._f("Achat", "", avail=COL)
        dc = _s(c.get("date_construction")); cstr = _s(c.get("constructeur"))
        self._f("Construction", dc + (f" par {cstr}" if cstr else ""), avail=COL)
        self._f("Taxe foncière", (_s(c.get("taxe_fonciere"))+" EUR") if c.get("taxe_fonciere") else "", avail=COL)

        # Assainissement
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Assainissement : ")+1
        self.cell(lbl_w, LHF, "Assainissement : ", ln=0)
        self._inline_fill(20, c.get("assainissement"))
        self.cell(3, LHF, "", ln=0)
        conf = c.get("assainissement_conforme")
        self._radio(["Conf.", "Non conf."],
                    selected="Conf." if conf is True else "Non conf." if conf is False else "")
        self.ln(LHF)

        self._f("Huisseries / matériaux", c.get("huisseries"), avail=COL)
        self._f("Exposition", c.get("exposition"), avail=COL)
        self._f("Chauffage / budget énergie", c.get("chauffage_budget"), avail=COL)

        # Terrain + Annexes
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Terrain : ")+1
        self.cell(lbl_w, LHF, "Terrain : ", ln=0)
        self._inline_fill(14, c.get("terrain_m2"))
        self.cell(self.get_string_width(" m²  ")+1, LHF, " m²  ", ln=0)
        self._chk(["Terrasse", "Garage", "Sous-sol"], checked=c.get("annexes") or [])
        self.ln(LHF)
        self._f("Autres annexes", c.get("autres_annexes"), avail=COL)

        # Mitoyenneté
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Mitoyenneté : ")+1
        self.cell(lbl_w, LHF, "Mitoyenneté : ", ln=0)
        mit = _s(c.get("mitoyennete")).lower()
        self._radio(["Oui", "Non"],
                    selected="Oui" if "oui" in mit else "Non" if "non" in mit else "")
        self.cell(3, LHF, "", ln=0)
        self._inline_label("Fondations")
        self._inline_fill((self.l_margin + COL) - self.get_x() - 0.5, c.get("fondations"))
        self.ln(LHF)

        # DPE / GES
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        self.cell(self.get_string_width("DPE : ")+1, LHF, "DPE : ", ln=0)
        self._inline_fill(8, c.get("dpe"))
        self.cell(2, LHF, "", ln=0)
        self.cell(self.get_string_width("GES : ")+1, LHF, "GES : ", ln=0)
        self._inline_fill(8, c.get("ges"))
        self.cell(2, LHF, "", ln=0)
        self._inline_label("Réal. le")
        self._inline_fill((self.l_margin + COL) - self.get_x() - 0.5, c.get("dpe_date"))
        self.ln(LHF)

        # Diagnostics
        self.set_font("R", "", FS_FIELD)
        self.set_text_color(*DGRAY)
        lbl_w = self.get_string_width("Diagnostics : ")+1
        self.cell(lbl_w, LHF, "Diagnostics : ", ln=0)
        self._chk(["Elec.", "Plomb", "Gaz", "Carrez", "Amiante"],
                  checked=c.get("diagnostics") or [])
        self.ln(LHF)

        self._f("Vis-à-vis / nuisances / vue", c.get("vis_a_vis"), avail=COL)
        self._f("Servitudes / PLU / remarques", c.get("servitudes"), avail=COL)

    # ── SURFACES ──────────────────────────────────────────────────────────────
    def _bloc_surfaces(self, d):
        s = d.get("surfaces") or {}
        self._sec(".surfaces", w=COL)
        # Pièces fixes
        pieces = [
            ("Entrée",         s.get("entree")),
            ("Séjour / salon", s.get("sejour_salon")),
            ("Salle à manger", s.get("salle_a_manger")),
            ("Cuisine",        s.get("cuisine")),
            ("Chambre(s)",     s.get("chambres")),
            ("S. de bains",    s.get("salle_de_bains")),
            ("Salle d'eau",    s.get("salle_d_eau")),
            ("WC indép.",      s.get("wc_independants")),
            ("Couloir / dég.", s.get("couloir")),
            ("Placards",       s.get("placards")),
        ]
        # Pièces supplémentaires issues des données
        for p in (s.get("autres") or []):
            nom = p.get("nom","") if isinstance(p, dict) else str(p)
            surf = p.get("surface","") if isinstance(p, dict) else ""
            if nom:
                pieces.append((nom, surf))
        # Lignes vides supplémentaires (à remplir à la main)
        while len(pieces) < 12:
            pieces.append(("Autre pièce", ""))

        hw = (COL - 1) / 2
        for i in range(0, len(pieces), 2):
            p1 = pieces[i]
            p2 = pieces[i+1] if i+1 < len(pieces) else None
            for p, is_left in [(p1, True), (p2, False)]:
                if p is None:
                    self.cell(hw, LHF - 0.3, "", ln=0)
                    continue
                self.set_font("R", "", FS_SMALL)
                lw = min(self.get_string_width(p[0]+" : ")+1, hw * 0.55)
                vw = hw - lw - 0.5
                self.set_text_color(*DGRAY)
                self.cell(lw, LHF - 0.3, p[0] + " : ", ln=0)
                x = self.get_x(); y = self.get_y()
                self.set_draw_color(*LGRAY)
                self.line(x, y + LHF - 0.8, x + vw, y + LHF - 0.8)
                self.set_text_color(*BLACK)
                self.cell(vw, LHF - 0.3, (" " + _s(p[1])) if p[1] else "", ln=0)
                if is_left:
                    self.cell(1, LHF - 0.3, "", ln=0)
            self.ln(LHF - 0.3)

        notes = _s(s.get("notes"))
        if notes:
            self.set_font("R", "", FS_SMALL)
            self.set_text_color(*DGRAY)
            self.cell(9, LHF - 0.5, "Notes :", ln=0)
            self.set_text_color(*BLACK)
            self.cell(COL - 10, LHF - 0.5, " " + notes[:70], new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        surf = _s(s.get("surface_habitable"))
        self.set_font("R", "B", FS_BIG)
        self.set_text_color(*TEAL_D)
        self.cell(COL, 6, f"Surface habitable : {surf} m²", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)

    # ── TRAVAUX ───────────────────────────────────────────────────────────────
    def _bloc_travaux(self, d):
        self._sec(".travaux réalisés", w=COL)
        self._travaux_lines(d.get("travaux", ""), n=9)

    # ── ESTIMATION ────────────────────────────────────────────────────────────
    def _bloc_estimation(self, d):
        self._sec(".estimation")
        est = d.get("estimation") or {}
        membres = [
            ("Quentin",  "Arthur"),
            ("Sébastien","Sonia"),
            ("Corentin", "Charlotte"),
            ("Romain",   "Marie"),
            ("Morgan",   "Carole"),
            ("Thomas",   "Hugo"),
        ]
        MCOL = (INNER_W - 6) / 2
        y_cur = self.get_y()
        for m1, m2 in membres:
            for m, xcol in [(m1, ML), (m2, ML + MCOL + 6)]:
                self.set_xy(xcol, y_cur)
                v = _s(est.get(m.lower()))
                self.set_font("R", "", FS_FIELD)
                label_w = self.get_string_width(m + " : ") + 1
                fill_w = MCOL - label_w - 1
                self.set_text_color(*DGRAY)
                self.cell(label_w, LHF, m + " : ", ln=0)
                x = self.get_x(); y = self.get_y()
                self.set_draw_color(*LGRAY)
                self.line(x, y + LHF - 0.5, x + fill_w, y + LHF - 0.5)
                self.set_text_color(*BLACK)
                self.cell(fill_w, LHF, " " + v, ln=0)
            y_cur += LHF
        self.set_xy(ML, y_cur + 2)
        prix = _s(d.get("prix_estimation"))
        self.set_font("R", "B", FS_BIG + 1)
        self.set_text_color(*TEAL_D)
        self.cell(52, 7, "Prix de l'estimation : ", ln=0)
        self.set_draw_color(*TEAL_D)
        x = self.get_x(); y = self.get_y()
        self.line(x, y + 6.5, x + 75, y + 6.5)
        self.cell(75, 7, prix, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*BLACK)
        self.set_draw_color(*BLACK)

    # ── OBSERVATIONS (remplit l'espace restant) ───────────────────────────────
    def _bloc_observations(self, d):
        y_now = self.get_y() + 2
        y_footer = H - MB - 2
        avail = y_footer - y_now
        if avail < 15:
            return
        self.set_xy(ML, y_now)
        self._divider(extra_below=2)
        self._sec(".observations / notes générales")
        y_after = self.get_y()
        remaining = y_footer - y_after - 2
        n_lines = max(2, int(remaining / LH))
        obs = _s(d.get("observations", ""))
        chars = int(INNER_W / 1.68)
        words = obs.split()
        lines_out = []
        cur = ""
        for w in words:
            if len(cur) + len(w) + 1 > chars:
                lines_out.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur: lines_out.append(cur)
        for i in range(n_lines):
            txt = lines_out[i] if i < len(lines_out) else ""
            self.set_draw_color(*LGRAY)
            self.line(self.get_x(), self.get_y() + LH - 0.3,
                      self.get_x() + INNER_W, self.get_y() + LH - 0.3)
            self.set_font("R", "", FS_FIELD)
            self.set_text_color(*BLACK)
            self.cell(INNER_W, LH, (" " + txt) if txt else "", new_x="LMARGIN", new_y="NEXT")

    # ── FOOTER ────────────────────────────────────────────────────────────────
    def _footer_bar(self):
        self.set_xy(ML, H - MB + 1)
        self.set_draw_color(*DIVIDER)
        self.line(ML, H - MB + 1, W - MR, H - MB + 1)
        self.set_xy(ML, H - MB + 2.5)
        self.set_font("R", "B", FS_SMALL - 0.5)
        self.set_text_color(*TEAL)
        self.cell(INNER_W / 2, 4, ".la petite agence  IMMOBILIER", ln=0)
        self.set_font("R", "", FS_SMALL - 1)
        self.set_text_color(*DGRAY)
        self.cell(INNER_W / 2, 4, "Document confidentiel — usage interne", align="R")

    # ════════════════════════════════════════════════════════════════════════
    #  GENERATE
    # ════════════════════════════════════════════════════════════════════════
    def generate(self, data: dict) -> bytes:
        self._header(data)
        self._adresse(data)
        self._divider()

        # Bloc 1 — 2 colonnes
        y1 = self.get_y()
        self.set_left_margin(ML)
        self.set_xy(ML, y1)
        self._bloc_vendeurs(data)
        y_left = self.get_y()

        self._col_right(y1)
        if self.type_bien == "maison":
            self._bloc_carac_maison(data)
        else:
            self._bloc_carac_appart(data)
        y_right = self.get_y()
        self._col_restore()

        self.set_xy(ML, max(y_left, y_right) + 2)
        self._divider()

        # Bloc 2 — 2 colonnes
        y2 = self.get_y()
        self.set_left_margin(ML)
        self.set_xy(ML, y2)
        self._bloc_surfaces(data)
        y_left2 = self.get_y()

        self._col_right(y2)
        self._bloc_travaux(data)
        y_right2 = self.get_y()
        self._col_restore()

        self.set_xy(ML, max(y_left2, y_right2) + 2)
        self._divider()

        # Estimation
        self.set_left_margin(ML)
        self._bloc_estimation(data)

        # Observations
        self._bloc_observations(data)

        # Footer
        self._footer_bar()

        return bytes(self.output())


def generate_pdf(data: dict) -> bytes:
    t = _s(data.get("type", "appartement")).lower()
    type_bien = "maison" if "maison" in t else "appartement"
    return Fiche(type_bien=type_bien).generate(data)

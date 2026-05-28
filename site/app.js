// Joy Division registre — logique Alpine.
//
// Charge data/all-variants.json, expose un store Alpine 'registry' avec
// l'etat UI (filtres, mode de vue) et les listes derivees reactives
// (filteredVariants, displayedRows, compteurs).

const ARTICLES = ["the ", "a ", "an ", "le ", "la ", "les ", "l'", "un ", "une "];

// Extrait l'ID Discogs (release ou master) depuis une URL.
// Couvre les deux formes : .../release/{id}-Slug et .../Slug/release/{id}.
const RELEASE_ID_RE = /\/(?:release|master)\/(\d+)/;

// ==========================================================================
// Pictogrammes de format
// ==========================================================================
//
// 16 SVG monochromes ou couleur representative inline (style Lucide :
// viewBox 24x24, stroke 1.5px). Pour le vinyle, le DISQUE porte une
// couleur de remplissage representative (ambre pour les colores, bleu
// pale a 60 % pour les transparents, pourpre pour les picture discs) ;
// le contour reste en currentColor pour s'adapter au theme. Tous les
// autres pictos restent strictement monochromes (currentColor).
//
// Cles utilisees par detectFormat() ci-dessous.

const FORMAT_ICONS = {
  "vinyl-12-black": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Zm-7.2 0a2.8 2.8 0 1 0-5.6 0 2.8 2.8 0 0 0 5.6 0Z" fill="currentColor" fill-rule="evenodd"/><circle cx="12" cy="12" r="0.8" fill="currentColor"/></svg>`,
  "vinyl-12-colored": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Zm-7.2 0a2.8 2.8 0 1 0-5.6 0 2.8 2.8 0 0 0 5.6 0Z" fill="#d97706" fill-opacity="0.8" stroke="currentColor" stroke-width="1" fill-rule="evenodd"/><circle cx="12" cy="12" r="0.8" fill="currentColor"/></svg>`,
  "vinyl-12-clear": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="9.5" fill="#93c5fd" fill-opacity="0.6" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="2.8" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="12" cy="12" r="0.8" fill="currentColor"/></svg>`,
  "vinyl-12-picture": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="9.5" fill="#7c3aed" fill-opacity="0.75" stroke="currentColor" stroke-width="1.5"/><circle cx="10.3" cy="10.4" r="0.9" fill="currentColor"/><path d="M8 14.5 L10.3 12.3 L12.2 14 L14 12.5 L16 14.5 Z" fill="currentColor"/></svg>`,
  "vinyl-10-black": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M20.5 12a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0Zm-6.1 0a2.4 2.4 0 1 0-4.8 0 2.4 2.4 0 0 0 4.8 0Z" fill="currentColor" fill-rule="evenodd"/><circle cx="12" cy="12" r="0.7" fill="currentColor"/></svg>`,
  "vinyl-10-colored": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M20.5 12a8.5 8.5 0 1 1-17 0 8.5 8.5 0 0 1 17 0Zm-6.1 0a2.4 2.4 0 1 0-4.8 0 2.4 2.4 0 0 0 4.8 0Z" fill="#d97706" fill-opacity="0.8" stroke="currentColor" stroke-width="1" fill-rule="evenodd"/><circle cx="12" cy="12" r="0.7" fill="currentColor"/></svg>`,
  "vinyl-10-clear": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="#93c5fd" fill-opacity="0.6" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="2.4" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="12" cy="12" r="0.7" fill="currentColor"/></svg>`,
  "vinyl-7-black": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M19.5 12a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Zm-5.5 0a2 2 0 1 0-4 0 2 2 0 0 0 4 0Z" fill="currentColor" fill-rule="evenodd"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/></svg>`,
  "vinyl-7-colored": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M19.5 12a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Zm-5.5 0a2 2 0 1 0-4 0 2 2 0 0 0 4 0Z" fill="#d97706" fill-opacity="0.8" stroke="currentColor" stroke-width="1" fill-rule="evenodd"/><circle cx="12" cy="12" r="0.6" fill="currentColor"/></svg>`,
  "cd": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="1"/><circle cx="12" cy="12" r="2" fill="none" stroke="currentColor" stroke-width="1"/></svg>`,
  "dvd": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="9.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="1"/><rect x="10.5" y="10.5" width="3" height="3" fill="currentColor"/></svg>`,
  "cassette-audio": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect x="3" y="6" width="18" height="12" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8.5" cy="12" r="2.2" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="15.5" cy="12" r="2.2" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="8.5" cy="12" r="0.6" fill="currentColor"/><circle cx="15.5" cy="12" r="0.6" fill="currentColor"/></svg>`,
  "cassette-video": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="6.5" y="9" width="11" height="6" rx="0.5" fill="none" stroke="currentColor" stroke-width="1.2"/><circle cx="9.5" cy="12" r="0.7" fill="currentColor"/><circle cx="14.5" cy="12" r="0.7" fill="currentColor"/></svg>`,
  "book": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M5 3 h11 a3 3 0 0 1 3 3 v15 a2 2 0 0 0 -2 -2 h-12 z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M5 3 v16" stroke="currentColor" stroke-width="1.5"/><path d="M5 19 h12" stroke="currentColor" stroke-width="1.3"/></svg>`,
  "magazine": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect x="4" y="3.5" width="16" height="17" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="7" y1="8" x2="17" y2="8" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="7" y1="11" x2="17" y2="11" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/><line x1="7" y1="14" x2="14" y2="14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>`,
  "generic": `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 1.6"/></svg>`,
};

// Libelles humains pour le tooltip (attribut title) sur le picto.
const FORMAT_LABELS = {
  "vinyl-12-black": "Vinyle 12\" noir",
  "vinyl-12-colored": "Vinyle 12\" coloré",
  "vinyl-12-clear": "Vinyle 12\" transparent",
  "vinyl-12-picture": "Picture disc 12\"",
  "vinyl-10-black": "Vinyle 10\" noir",
  "vinyl-10-colored": "Vinyle 10\" coloré",
  "vinyl-10-clear": "Vinyle 10\" transparent",
  "vinyl-7-black": "Vinyle 7\" noir",
  "vinyl-7-colored": "Vinyle 7\" coloré",
  "cd": "CD",
  "dvd": "DVD",
  "cassette-audio": "Cassette audio",
  "cassette-video": "Vidéo (VHS / DVD / Blu-ray)",
  "book": "Livre",
  "magazine": "Magazine / fanzine",
  "generic": "Format indéterminé",
};

// Detecte la categorie de pictogramme a afficher pour une variante.
// release_type est l'autorite pour les categories non-musique (livre,
// magazine, video). Pour l'audio, on inspecte format_details.supports[0]
// (le dataset n'a aucun variant avec >1 support a ce jour).
function detectFormat(variant) {
  if (!variant) return "generic";
  const rt = variant.release_type;
  const fd = variant.format_details || {};

  // Imprimes
  if (rt === "livre" || fd.type === "book") return "book";
  if (rt === "para" || fd.type === "para") return "magazine";

  // Video (tous supports VHS/DVD/Blu-ray simplifies en un picto)
  if (rt === "video" || fd.type === "video") return "cassette-video";

  // Audio : detail par support_type
  const sup = (fd.supports && fd.supports[0]) || {};
  const support = (sup.support_type || "").toLowerCase();
  const size = sup.size; // typiquement '12"', '10"', '7"' ou null
  const color = (sup.color || "").toLowerCase();

  if (support === "cassette") return "cassette-audio";
  if (support === "cd") return "cd";
  // DVD/Bluray ne devraient pas tomber ici (couvert par video plus haut)
  // mais filet pour les rares cas mixtes
  if (support === "dvd" || support === "bluray" || support === "vhs") return "cassette-video";

  if (support === "vinyl" || support === "flexi") {
    // Detection de taille -- 14 variants en 10" tombaient sur vinyl-12-*
    // dans la version initiale, d'ou une contradiction picto/texte format.
    const is7 = size === "7\"" || size === '7"' || size === "7";
    const is10 = size === "10\"" || size === '10"' || size === "10";
    const sizeSlot = is7 ? "7" : is10 ? "10" : "12";

    // Picture disc et clear ne sont pas distingues en 7"/10" : rabattus
    // sur "-colored" en 7" (peu de cas) et sur "-clear" en 10" (cas
    // "clear" represente, "picture" absent du jeu de donnees).
    if (color.includes("picture")) {
      if (sizeSlot === "12") return "vinyl-12-picture";
      return sizeSlot === "7" ? "vinyl-7-colored" : "vinyl-10-colored";
    }
    if (color.includes("clear") || color.includes("transparent")) {
      if (sizeSlot === "7") return "vinyl-7-colored";
      return sizeSlot === "10" ? "vinyl-10-clear" : "vinyl-12-clear";
    }
    // Detection explicite d'une couleur ou d'un pattern colore. Necessaire
    // pour les splatters et mixtes type "splatter green black" ou
    // "black silver" qui contiennent "black" mais sont visuellement des
    // disques colores -- la branche "black par defaut" plus bas les
    // capturait a tort.
    const COLOR_KEYWORDS = [
      "orange", "red", "yellow", "green", "blue", "purple", "pink",
      "violet", "turquoise", "magenta", "amber", "gold", "silver",
      "white", "brown",
      "swirl", "splatter", "marble", "marbled",
    ];
    if (color && COLOR_KEYWORDS.some(kw => color.includes(kw))) {
      return `vinyl-${sizeSlot}-colored`;
    }
    if (color && !color.includes("black") && !color.includes("noir")) {
      return `vinyl-${sizeSlot}-colored`;
    }
    return `vinyl-${sizeSlot}-black`;
  }

  return "generic";
}

function extractReleaseId(url) {
  if (!url) return null;
  const m = RELEASE_ID_RE.exec(url);
  return m ? m[1] : null;
}

function sortKey(title) {
  if (!title) return "";
  let s = String(title).toLowerCase().trim();
  for (const art of ARTICLES) {
    if (s.startsWith(art)) {
      return s.substring(art.length).trim();
    }
  }
  return s;
}

function formatSupports(supports) {
  if (!Array.isArray(supports) || supports.length === 0) return "";
  return supports.map(s => {
    const count = s.count ?? 1;
    const t = s.support_type ?? "?";
    const size = s.size ? ` ${s.size}` : "";
    const color = s.color ? ` ${s.color}` : "";
    return `${count}× ${t}${size}${color}`;
  }).join(" + ");
}

function formatSummary(variant) {
  const fd = variant.format_details;
  if (!fd) return "";
  if (fd.type === "audio" || fd.type === "video") return formatSupports(fd.supports);
  if (fd.type === "book") return `livre · ${fd.format_physical ?? ""}`;
  if (fd.type === "para") return `para · ${fd.parent_object ?? ""}`;
  if (fd.type === "box") return `coffret · ${fd.components?.length ?? 0} composants`;
  return fd.type ?? "";
}

function yamlDump(obj, indent = 0) {
  // Mini YAML dumper, suffisant pour afficher format_details lisiblement.
  if (obj === null || obj === undefined) return "null";
  const pad = "  ".repeat(indent);
  if (Array.isArray(obj)) {
    if (obj.length === 0) return "[]";
    return obj.map(item => {
      if (item !== null && typeof item === "object") {
        const lines = yamlDump(item, indent + 1).split("\n");
        return `${pad}- ${lines[0].trimStart()}\n${lines.slice(1).map(l => `${pad}  ${l.trimStart()}`).join("\n")}`.replace(/\n\s*$/, "");
      }
      return `${pad}- ${yamlScalar(item)}`;
    }).join("\n");
  }
  if (typeof obj === "object") {
    const keys = Object.keys(obj);
    if (keys.length === 0) return "{}";
    return keys.map(k => {
      const v = obj[k];
      if (v !== null && typeof v === "object") {
        if (Array.isArray(v) && v.length === 0) return `${pad}${k}: []`;
        if (!Array.isArray(v) && Object.keys(v).length === 0) return `${pad}${k}: {}`;
        return `${pad}${k}:\n${yamlDump(v, indent + 1)}`;
      }
      return `${pad}${k}: ${yamlScalar(v)}`;
    }).join("\n");
  }
  return yamlScalar(obj);
}

function yamlScalar(v) {
  if (v === null || v === undefined) return "null";
  if (typeof v === "string") {
    if (v === "" || /[:#\n]|^\s|\s$/.test(v)) return JSON.stringify(v);
    return v;
  }
  return String(v);
}

function registerRegistryStore() {
  Alpine.store("registry", {
    // ===== etat brut =====
    data: null,
    loading: true,
    loadError: null,
    // Compte total des membres par group_id (depuis data.variant_groups,
    // donc independant des filtres). Permet d'afficher 'K/N variantes'
    // sur la ligne consolidee quand un filtre reduit la visibilite.
    groupTotalCounts: {},
    // Mapping release_id -> chemin de cover (relatif a site/), charge
    // depuis data/covers-index.json. Pris en charge par coverFor().
    coversIndex: {},

    // ===== filtres / UI =====
    search: "",
    releaseTypes: [],
    letter: null,
    withDiscogs: false,
    withJoydiv: false,
    groupedView: false,
    expandedGroups: {},
    selectedVariant: null,

    async init() {
      try {
        // all-variants.json est requis ; covers-index.json est facultatif
        // (s'il manque, on degrade en n'affichant pas de vignette plutot
        // que d'echouer le chargement complet).
        const [variantsResp, coversResp] = await Promise.all([
          fetch("data/all-variants.json"),
          fetch("data/covers-index.json").catch(() => null),
        ]);
        if (!variantsResp.ok) {
          this.loadError = `HTTP ${variantsResp.status} en chargeant data/all-variants.json`;
          this.loading = false;
          return;
        }
        const data = await variantsResp.json();
        // Sort variants once at load for stable ordering.
        data.variants.sort((a, b) => {
          const ka = sortKey(a.canonical_title);
          const kb = sortKey(b.canonical_title);
          if (ka < kb) return -1;
          if (ka > kb) return 1;
          return (a.variant_id || "").localeCompare(b.variant_id || "");
        });
        this.data = data;
        // Build group total-count lookup once for K/N labels.
        for (const g of data.variant_groups ?? []) {
          this.groupTotalCounts[g.group_id] = g.count;
        }
        if (coversResp && coversResp.ok) {
          this.coversIndex = await coversResp.json();
        }
      } catch (err) {
        this.loadError = `Erreur de chargement : ${err.message}`;
      } finally {
        this.loading = false;
      }
    },

    // Retourne le chemin de la cover Discogs d'une variante, ou null.
    // Joint via discogs_url -> release_id -> coversIndex.
    coverFor(variant) {
      if (!variant?.discogs_url) return null;
      const rid = extractReleaseId(variant.discogs_url);
      if (!rid) return null;
      return this.coversIndex[rid] ?? null;
    },

    // ===== actions UI =====

    toggleReleaseType(rt) {
      const i = this.releaseTypes.indexOf(rt);
      if (i >= 0) this.releaseTypes.splice(i, 1);
      else this.releaseTypes.push(rt);
    },

    setLetter(letter) {
      this.letter = this.letter === letter ? null : letter;
    },

    toggleGroupedView() {
      this.groupedView = !this.groupedView;
      this.expandedGroups = {};
    },

    toggleGroup(gid) {
      this.expandedGroups[gid] = !this.expandedGroups[gid];
    },

    selectVariant(v) {
      this.selectedVariant = v;
    },

    resetFilters() {
      this.search = "";
      this.releaseTypes = [];
      this.letter = null;
      this.withDiscogs = false;
      this.withJoydiv = false;
    },

    get hasActiveFilters() {
      return !!(this.search || this.releaseTypes.length > 0 || this.letter
        || this.withDiscogs || this.withJoydiv);
    },

    // ===== derivees =====

    get filteredVariants() {
      if (!this.data) return [];
      const needle = this.search.trim().toLowerCase();
      const types = this.releaseTypes;
      const letter = this.letter;
      const requireDisc = this.withDiscogs;
      const requireJoy = this.withJoydiv;

      return this.data.variants.filter(v => {
        if (types.length > 0 && !types.includes(v.release_type)) return false;
        if (letter !== null && v.joydiv_letter !== letter) return false;
        if (requireDisc && !v.discogs_url) return false;
        if (requireJoy && !v.joydiv_url) return false;
        if (needle) {
          const fields = [
            v.canonical_title,
            v.canonical_artist,
            v.country_or_pressing_place,
            v.notes,
            v.variant_id,
          ].filter(Boolean).map(s => String(s).toLowerCase());
          const fd = v.format_details;
          if (fd?.supports) {
            for (const s of fd.supports) {
              if (s.color) fields.push(String(s.color).toLowerCase());
              if (s.support_type) fields.push(String(s.support_type).toLowerCase());
            }
          }
          if (!fields.some(f => f.includes(needle))) return false;
        }
        return true;
      });
    },

    get visibleCount() {
      return this.filteredVariants.length;
    },

    get visibleGroupCount() {
      const seen = new Set();
      let standalone = 0;
      for (const v of this.filteredVariants) {
        if (v.variant_group?.group_id) seen.add(v.variant_group.group_id);
        else standalone += 1;
      }
      return seen.size + standalone;
    },

    get formattedGeneratedAt() {
      if (!this.data?.generated_at) return "";
      try {
        const d = new Date(this.data.generated_at);
        return d.toISOString().substring(0, 10);
      } catch {
        return this.data.generated_at;
      }
    },

    // displayedRows : liste de lignes preparees pour le template.
    //   - mode eclate : 1 row par variant.
    //   - mode consolide : 1 row par variant_group + variants standalone,
    //     avec lignes membres expandees sur demande.
    get displayedRows() {
      const variants = this.filteredVariants;
      if (!this.groupedView) {
        return variants.map(v => this._variantRow(v));
      }

      // Mode consolide : regroupe par variant_group.group_id.
      const groupBuckets = new Map();
      const standalone = [];
      for (const v of variants) {
        const gid = v.variant_group?.group_id;
        if (gid) {
          if (!groupBuckets.has(gid)) groupBuckets.set(gid, []);
          groupBuckets.get(gid).push(v);
        } else {
          standalone.push(v);
        }
      }

      // Assemble en preservant l'ordre alphabetique du titre du 1er
      // membre de chaque groupe / du standalone.
      const entries = [];
      for (const [gid, members] of groupBuckets) {
        entries.push({ key: sortKey(members[0].canonical_title), isGroup: true, gid, members });
      }
      for (const v of standalone) {
        entries.push({ key: sortKey(v.canonical_title), isGroup: false, variant: v });
      }
      entries.sort((a, b) => a.key.localeCompare(b.key));

      const rows = [];
      for (const e of entries) {
        if (e.isGroup) {
          rows.push(this._groupRow(e.gid, e.members));
          if (this.expandedGroups[e.gid]) {
            for (const m of e.members) {
              rows.push(this._variantRow(m, /* isMember= */ true));
            }
          }
        } else {
          rows.push(this._variantRow(e.variant));
        }
      }
      return rows;
    },

    _variantRow(v, isMember = false) {
      const fmtKey = detectFormat(v);
      return {
        key: `v-${v.variant_id}`,
        isGroup: false,
        isMember,
        variant: v,
        title: v.canonical_title,
        release_type: v.release_type,
        year: v.year,
        country: v.country_or_pressing_place,
        formatSummary: formatSummary(v),
        formatIcon: FORMAT_ICONS[fmtKey] || FORMAT_ICONS.generic,
        formatLabel: FORMAT_LABELS[fmtKey] || FORMAT_LABELS.generic,
        cover: this.coverFor(v),
      };
    },

    _groupRow(gid, members) {
      // Cover representative : premier membre du groupe qui en a une
      // (fallback sur le 1er membre meme sans cover, pour les autres
      // champs derives).
      const first = members[0];
      const coverMember = members.find(m => this.coverFor(m)) ?? first;
      const expanded = !!this.expandedGroups[gid];
      const store = this;
      // K = membres du groupe qui passent les filtres courants ;
      // N = total des membres dans le groupe (data brute).
      // Label "N variantes" si tous matchent, "K/N variantes" sinon,
      // singulier si K === 1.
      const K = members.length;
      const N = this.groupTotalCounts[gid] ?? K;
      let memberCountLabel;
      if (K === N) {
        memberCountLabel = `${N} variantes`;
      } else if (K === 1) {
        memberCountLabel = `1/${N} variante`;
      } else {
        memberCountLabel = `${K}/${N} variantes`;
      }
      return {
        key: `g-${gid}`,
        isGroup: true,
        isMember: false,
        variant: null,
        group_id: gid,
        members,
        memberCount: K,
        memberCountTotal: N,
        memberCountLabel,
        expanded,
        title: first.canonical_title,
        release_type: first.release_type,
        year: first.year,
        country: first.country_or_pressing_place,
        formatSummary: formatSummary(first),
        formatIcon: FORMAT_ICONS[detectFormat(first)] || FORMAT_ICONS.generic,
        formatLabel: FORMAT_LABELS[detectFormat(first)] || FORMAT_LABELS.generic,
        cover: this.coverFor(coverMember),
        toggleExpand() { store.toggleGroup(gid); },
      };
    },

    yamlFor(obj) {
      return yamlDump(obj);
    },

    // Injecte une chaine SVG dans l'element fourni en garantissant le
    // namespace SVG. La technique : creer un conteneur <svg> via
    // createElementNS (donc dans le bon namespace ET dans le document
    // courant -- pas de cross-document transfer), recopier les
    // attributs racine du source, puis poser le contenu enfant via
    // innerHTML SUR L'ELEMENT SVG. Quand le parent est SVG-namespaced,
    // le parser HTML5 bascule en regles SVG pour les enfants, donc
    // <path>/<circle>/<rect> sont correctement crees dans le namespace
    // SVG. C'est l'approche standard pour injection SVG dynamique
    // (utilisee par svg.js, raphaeljs, lit-html, etc.).
    //
    // Historique : x-html (innerHTML direct sur un span) deposait un
    // <svg> sans ses enfants ; DOMParser + appendChild cross-document
    // donnait un <svg> sans rendu visible. Cette approche contourne
    // les deux pieges.
    injectSvg(el, svgString) {
      if (!el) return;
      while (el.firstChild) el.removeChild(el.firstChild);
      if (!svgString) return;
      const ns = "http://www.w3.org/2000/svg";
      try {
        const svg = document.createElementNS(ns, "svg");
        const attrMatch = /<svg\b([^>]*)>/i.exec(svgString);
        if (attrMatch) {
          const attrRe = /([a-zA-Z_][\w:-]*)\s*=\s*"([^"]*)"/g;
          let m;
          while ((m = attrRe.exec(attrMatch[1])) !== null) {
            // xmlns deja porte par createElementNS, on le saute.
            if (m[1].toLowerCase() !== "xmlns") svg.setAttribute(m[1], m[2]);
          }
        }
        const innerMatch = /<svg\b[^>]*>([\s\S]*)<\/svg>/i.exec(svgString);
        if (innerMatch) svg.innerHTML = innerMatch[1];
        el.appendChild(svg);
      } catch (e) {
        // Visible en console pour reperer une regression future, mais
        // sans casser le rendu de la table -- la cellule reste vide.
        console.warn("injectSvg failed:", e);
      }
    },
  });

  // Bootstrap : charge les donnees des l'initialisation du store.
  Alpine.store("registry").init();
}

// Pattern d'enregistrement defensif : si Alpine est deja initialise au
// moment ou ce script s'execute (peut arriver selon l'ordre des balises
// <script> ou le mode de chargement), on enregistre immediatement ;
// sinon on attend l'evenement 'alpine:init' qui se declenche AVANT que
// Alpine ne process le DOM.
if (window.Alpine) {
  registerRegistryStore();
} else {
  document.addEventListener("alpine:init", registerRegistryStore);
}

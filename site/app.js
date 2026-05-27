// Joy Division registre — logique Alpine.
//
// Charge data/all-variants.json, expose un store Alpine 'registry' avec
// l'etat UI (filtres, mode de vue) et les listes derivees reactives
// (filteredVariants, displayedRows, compteurs).

const ARTICLES = ["the ", "a ", "an ", "le ", "la ", "les ", "l'", "un ", "une "];

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
        const resp = await fetch("data/all-variants.json");
        if (!resp.ok) {
          this.loadError = `HTTP ${resp.status} en chargeant data/all-variants.json`;
          this.loading = false;
          return;
        }
        const data = await resp.json();
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
      } catch (err) {
        this.loadError = `Erreur de chargement : ${err.message}`;
      } finally {
        this.loading = false;
      }
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
      };
    },

    _groupRow(gid, members) {
      const first = members[0];
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
        toggleExpand() { store.toggleGroup(gid); },
      };
    },

    yamlFor(obj) {
      return yamlDump(obj);
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

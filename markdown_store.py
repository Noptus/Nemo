import os, yaml, datetime as dt
DECAY_HALFLIFE_DAYS     = 7          # halve every week
MAX_TOKENS_AT_STRENGTH1 = 1600
MIN_STRENGTH            = 0.05

class MarkdownStore:
    def __init__(self, base_path="kg"):
        self.base = base_path
        os.makedirs(self.base, exist_ok=True)

    # ---------------- helpers ----------------
    def _path(self, key): return f"{self.base}/{key}.md"
    def _now(self):       return dt.datetime.utcnow().isoformat()

    def _truncate(self, text, strength):
        cap = int(MAX_TOKENS_AT_STRENGTH1 * strength)
        return " ".join(text.split()[:cap])

    # ---------------- API --------------------
    async def put(self, *, key: str, value: dict, **_):
        meta      = value.get("meta", {})
        strength  = float(meta.get("strength", 0.3))
        body      = self._truncate(value["text"], strength)
        meta.update({"strength": strength, "updated": self._now()})
        with open(self._path(key), "w") as f:
            f.write("---\n"+yaml.safe_dump(meta)+"---\n"+body)

    async def search(self, query, k=5, **_):
        # *tiny* semantic+strength ranking; good enough for demo
        from sentence_transformers import SentenceTransformer, util
        enc  = SentenceTransformer("all-MiniLM-L6-v2")
        qvec = enc.encode(query, convert_to_tensor=True)
        hits = []
        for file in os.listdir(self.base):
            meta, text = yaml.safe_load_all(open(self._path(file[:-3])))[0]
            svec = enc.encode(text, convert_to_tensor=True)
            score = float(util.cos_sim(qvec, svec))*0.7 + meta["strength"]*0.3
            hits.append((score, text))
        hits.sort(reverse=True)
        return [t for _, t in hits[:k]]

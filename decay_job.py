import os, yaml, math, datetime as dt
from markdown_store import DECAY_HALFLIFE_DAYS, MIN_STRENGTH, MAX_TOKENS_AT_STRENGTH1

BASE = "kg"
now  = dt.datetime.utcnow()

for fn in list(os.listdir(BASE)):
    path = f"{BASE}/{fn}"
    meta, body = yaml.safe_load_all(open(path))[0]
    age_days   = (now - dt.datetime.fromisoformat(meta["updated"])).days
    meta["strength"] *= 0.5 ** (age_days / DECAY_HALFLIFE_DAYS)
    if meta["strength"] < MIN_STRENGTH:
        os.remove(path)                      # forgotten
        continue
    # shrink body if weaker
    tok_cap = int(MAX_TOKENS_AT_STRENGTH1 * meta["strength"])
    body    = " ".join(body.split()[:tok_cap])
    with open(path, "w") as f:
        f.write("---\n"+yaml.safe_dump(meta)+"---\n"+body)

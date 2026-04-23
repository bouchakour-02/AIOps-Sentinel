import re
import random
import pandas as pd

INPUT_FILE = "log-dataset.md"
OUTPUT_FILE = "vermeg-logs-train.csv"
TARGET_SIZE = 5000

# -----------------------------
# Text variations (important)
# -----------------------------
SYNONYMS = {
    "error": ["error", "failure", "exception"],
    "failed": ["failed", "crashed", "stopped"],
    "timeout": ["timeout", "delayed", "took too long"],
    "connection": ["connection", "link", "network"],
    "database": ["database", "db", "storage"],
    "memory": ["memory", "ram", "heap"],
    "cpu": ["cpu", "processor"],
}

ERROR_PATTERNS = [
    "ERROR connection failed to database",
    "FATAL system crash detected",
    "ERROR timeout while connecting to service",
    "CRITICAL memory overflow detected",
    "ERROR unable to allocate memory",
]

NORMAL_PATTERNS = [
    "INFO request completed successfully",
    "INFO database query executed",
    "INFO service running normally",
    "INFO health check passed",
    "INFO operation completed",
]

# -----------------------------
# Cleaning
# -----------------------------
def normalize_log(text):
    text = text.lower()
    text = re.sub(r'\d+', ' NUM ', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# -----------------------------
# Augmentation logic
# -----------------------------
def mutate_log(log):
    words = log.split()
    new_words = []

    for w in words:
        if w in SYNONYMS and random.random() < 0.3:
            new_words.append(random.choice(SYNONYMS[w]))
        else:
            new_words.append(w)

    # random number injection
    if random.random() < 0.3:
        new_words.append(str(random.randint(1, 100)))

    return " ".join(new_words)

def generate_dataset(base_logs):
    augmented = []

    for _ in range(TARGET_SIZE):
        if random.random() < 0.5:
            log = random.choice(base_logs)
            log = mutate_log(log)
            label = 1 if any(x in log.lower() for x in ["error", "fail", "fatal"]) else 0
        else:
            if random.random() < 0.5:
                log = random.choice(ERROR_PATTERNS)
                label = 1
            else:
                log = random.choice(NORMAL_PATTERNS)
                label = 0

        augmented.append({
            "raw_log": log,
            "label": label
        })

    return pd.DataFrame(augmented)

# -----------------------------
# Extract logs from md
# -----------------------------
def extract_logs(filepath):
    logs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if len(line) > 10 and not line.startswith("#"):
                logs.append(line)
    return logs

# -----------------------------
# MAIN
# -----------------------------
base_logs = extract_logs(INPUT_FILE)
df_aug = generate_dataset(base_logs)

df_aug["raw_norm"] = df_aug["raw_log"].apply(normalize_log)

df_aug.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Generated {len(df_aug)} logs → {OUTPUT_FILE}")
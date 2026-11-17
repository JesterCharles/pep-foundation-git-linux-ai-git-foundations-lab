# Grader image referenced by .evolv/grade.yml (image: "evolv/python-3.12").
# Dependencies are baked in so grading runs offline and fast.
#
#   docker build -t evolv/python-3.12 .
#
FROM python:3.12-slim

# This is a Git lab: the checks run git against the learner's lab repository.
# python:3.12-slim ships without Git, so install it here, at build time, so
# grading never needs the network.
RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work

# Bake dependencies into the image so `setup` in grade.yml is a no-op cache hit
# and grading needs no network access.
COPY requirements.txt /work/requirements.txt
RUN pip install --no-cache-dir -r /work/requirements.txt

# Learner fork + canonical tests are mounted/copied in at grade time.
CMD ["python", "-m", "pytest", "-q", "--junitxml=reports/out.xml"]

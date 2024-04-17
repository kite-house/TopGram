web: gunicorn 'name-of-application.wsgi'

#10 ERROR: process "/bin/bash -ol pipefail -c python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt" did not complete successfully: exit code: 1

 

-----

> [stage-0 6/8] RUN --mount=type=cache,id=s/0889caaa-91f3-4695-8a3d-e54a62b38a83-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt:

12.28 error: subprocess-exited-with-error

12.28

12.28 × Getting requirements to build wheel did not run successfully.

12.28 │ exit code: 1

12.28 ╰─> See above for output.

12.28

12.28 note: This error originates from a subprocess, and is likely not a problem with pip.

12.29

12.29 [notice] A new release of pip is available: 23.0.1 -> 24.0

12.29 [notice] To update, run: pip install --upgrade pip

-----

 

Dockerfile:20

-------------------

18 |     ENV NIXPACKS_PATH /opt/venv/bin:$NIXPACKS_PATH

19 |     COPY . /app/.

20 | >>> RUN --mount=type=cache,id=s/0889caaa-91f3-4695-8a3d-e54a62b38a83-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt

21 |

22 |

-------------------

ERROR: failed to solve: process "/bin/bash -ol pipefail -c python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt" did not complete successfully: exit code: 1

 

Error: Docker build failed
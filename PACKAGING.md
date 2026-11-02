# NavDP inference package

This fork makes the existing NavDP inference code installable as
`navdp-policy`, imported as `navdp_policy`. It does not duplicate the policy
sources: Hatchling maps `baselines/navdp/` into the installed namespace.
The original simulator and server remain source-checkout tools.

## Install

From this checkout into an existing Python 3.10+ environment:

```sh
uv pip install .
```

A consuming uv project can pin a **pushed** revision of this fork without a
submodule (replace `FULL_COMMIT_ID` with that revision):

```sh
uv add navdp-policy --git https://github.com/SikongJueluo/NavDP --rev FULL_COMMIT_ID
```

That command updates the consumer's `pyproject.toml` and `uv.lock`. Subsequent
`uv sync --locked` installs that pinned revision. Moving the fork forward does
not silently upgrade existing consumers. No PyPI publication is required.

```python
from navdp_policy import NavDP_Agent
```

Checkpoints must be provided separately via the existing `navi_model` argument.
They are never downloaded by importing or installing this package. The wheel
contains only the policy and its vendored Depth Anything implementation;
Flask, Gradio, IsaacSim and demo dependencies are not installed.

The initial tested consumer uses Python 3.10, torch 2.7.1,
torchvision 0.22.1, diffusers 0.33.1 and NumPy 2.2.6. Other metadata-compatible
versions are not all validated. GPU-specific torch indexes belong to the
consumer, not this library. `diffusers` remains pinned to the tested 0.33.1.

## Existing scripts and known limitations

The upstream source-checkout workflow is preserved:

```sh
cd baselines/navdp
python navdp_server.py --port 8888 --checkpoint /absolute/path/to/model.ckpt
```

Install that workflow's server dependencies separately using its original
requirements. Package imports use relative module names; top-level imports
continue to work for existing scripts. Installed wheels do not expose
`policy_agent`, `policy_network`, `policy_backbone` or `depth_anything` as
standalone top-level modules.

The upstream tree contains a LoGoPlanner Pi3 gitlink without `.gitmodules`.
This fork restores its URL and sets `update = none`, so uv's automatic
submodule initialization does not fetch an unrelated model repository.
To opt in when developing LoGoPlanner, run from the repository root:

```sh
git submodule update --init --checkout -- baselines/logoplanner/Pi3
```

This is a packaging change, not a model fix. The upstream positional `device`
argument bug and colormap registry access remain unchanged; consumers such as
Mini-Nav must retain their existing device/plotting compatibility handling.
No new model compatibility is claimed. Regular wheel/Git installs are the
supported consumption path; editable installs are not validated.

## Build and check

```sh
uv build
python -m unittest discover -s tests -v
```

Run the integration tests in an environment with the declared inference
dependencies already installed and `uv` on PATH. They build a fresh wheel,
install it into a temporary target with `--no-deps`, verify its contents, and
import it in isolated subprocesses outside the checkout. They also exercise
the original top-level script imports. They do not download model weights or
require scene data. Build dependencies are resolved in a temporary uv cache.

For a release, also rebuild a wheel from the sdist, test installation through
a fixed Git revision, check checkpoint parameter coverage, and compare seeded
point-goal outputs with the previous validated version. A one-step CPU smoke
is not evidence for every device, goal mode or multi-step navigation episode.

## Update from upstream

Keep the full upstream tree in this fork and merge upstream changes normally;
do not overwrite it with a second generated snapshot. There are no policy
files to recopy. Review conflicts in the three policy import blocks and build
metadata. New inference modules beneath the vendored Depth Anything directory
are included automatically; new policy modules require updating the explicit
file-selection lists in `pyproject.toml`.

After merging, rerun the build/import checks and model regressions, update the
package version for a new tested release, and push only when ready. Then
advance the consumer's pinned revision and refresh its lockfile. A changed
checkpoint or model behavior is a separate update, not a packaging side effect.

See `NOTICE.md`, `LICENSE`, and the vendored Depth Anything license for source
attribution and redistribution terms. The policy is not relicensed under a
permissive license by this fork.

# kernel/steamling - the shared kernel for SM8250, SM8650 and SM8750

This tree is Steamling's combined Qualcomm handheld kernel, built from the one in
[armada](https://github.com/armada-os/armada) (its packages/kernel directory at armada commit
`64207e61a3c5`, plus their iris low-latency decode patches from `ecc0d3e`, numbered `125a`-`125h`
so they sit where armada's series puts them), carried in Steamling's layout so `scripts/build-kernel.sh` builds it like any
other tree. The SM8550 family keeps its own ROCKNIX-synced tree in `kernel/sm8550/`.

Each SoC on it has only a `kernel/<soc>/kernel.conf`, which names this tree (`KERNEL_TREE=steamling`),
repeats the source pin and lists the dtb name prefixes its boot image ships
(`KERNEL_DTB_PREFIXES`). `make sync` does not touch this tree.

## What's here and where it came from

- `patches/10-steamling/` - armada's `patches/series`, in order (the `NNN-` prefix keeps the
  series order under the build's sort), rebased by hand onto Linux 7.3: the patches 7.3 already
  carries are gone and a few are adjusted to 7.3's code (the kernel (steamling) row of
  [PATCHES.md](../../PATCHES.md) lists them). armada's `PATCHES.md` records each patch's origin.
- `dts/qcom/` - armada's board device trees with armada's `dts/*.patch` deltas already applied.
- `kernel/steamling/config/linux.aarch64.conf` - arm64 `defconfig` plus armada's
  `armada-kernel.config.overrides`, resolved at 7.2.11; olddefconfig carries it to 7.3. build-kernel.sh then
  applies Steamling's usual deltas (sched_ext, BTF, binder, HZ 1000 and the rest) on top.
- `common-skip` - the `kernel/common` patches armada already carries.
- `config-assert` - what must be built in, since Steamling boots without an initramfs.

## Moving it

To take a newer armada: refresh `patches/10-steamling/` from their `patches/series` against the
pinned kernel version (fix or drop what no longer applies), copy their `dts/` with the deltas
applied, regenerate the config the same way, and recheck `common-skip`. Then bump
`KERNEL_VERSION`/`KERNEL_SOURCE_SHA256`/`KERNEL_PKGREL` in every `kernel/<soc>/kernel.conf`
that names this tree.

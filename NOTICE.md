# Source and license notices

This fork packages the inference policy from
[InternRobotics/NavDP](https://github.com/InternRobotics/NavDP), by Wenzhe Cai,
Jiaqi Peng, Yuqiang Yang, Yujian Zhang, Meng Wei, Hanqing Wang, Yilun Chen,
Tai Wang and Jiangmiao Pang. The initial packaging baseline is
`bff5eb8857f50e082243fb455d312409daabc3aa`.

The upstream README licenses the NavDP code under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
The full license is included in `LICENSE`; noncommercial and share-alike
conditions remain applicable. This fork does not relicense upstream code.

The vendored Depth Anything V2 implementation under
`baselines/navdp/depth_anything/depth_anything_v2/` retains its original
copyright notices and Apache-2.0 license at
`baselines/navdp/depth_anything/LICENSE`. Both license files ship with the
Python distributions.

Packaging changes add build metadata and a package entry point, and make
three policy imports relative when used as a package. Standalone script
imports remain supported. The model architecture, numerical operations,
parameters and vendored Depth Anything code are unchanged.

No checkpoint, training data, scene asset, IsaacSim code or server is
included in the Python wheel. The original research citation and complete
project documentation remain in the upstream README.

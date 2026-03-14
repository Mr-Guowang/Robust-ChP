<!-- PROJECT SHIELDS -->

<p align="center">
  <a href="https://github.com/Mr-Guowang/Robust-ChP/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/Mr-Guowang/Robust-ChP.svg?style=for-the-badge" alt="Contributors">
  </a>
  <a href="https://github.com/Mr-Guowang/Robust-ChP/network/members">
    <img src="https://img.shields.io/github/forks/Mr-Guowang/Robust-ChP.svg?style=for-the-badge" alt="Forks">
  </a>
  <a href="https://github.com/Mr-Guowang/Robust-ChP/stargazers">
    <img src="https://img.shields.io/github/stars/Mr-Guowang/Robust-ChP.svg?style=for-the-badge" alt="Stargazers">
  </a>
  <a href="https://github.com/Mr-Guowang/Robust-ChP/issues">
    <img src="https://img.shields.io/github/issues/Mr-Guowang/Robust-ChP.svg?style=for-the-badge" alt="Issues">
  </a>
  <a href="https://github.com/Mr-Guowang/Robust-ChP/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Mr-Guowang/Robust-ChP.svg?style=for-the-badge" alt="License">
  </a>
</p>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Mr-Guowang/Robust-ChP">
    <img src="logo.png" alt="Logo" width="600" height="600">
  </a>

  <h3 align="center">A plug-and-play robust choroid plexus segmentation tool</h3>

  <p align="center">
    We will continuously maintain this repository, and the dataset is being prepared for open release.
    <br />
    <a href="https://github.com/Mr-Guowang/Robust-ChP">Dataset</a>
    &middot;
    <a href="https://github.com/Mr-Guowang/Robust-ChP">Paper(under review)</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#Latest Updates">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## Latest Updates

> **Maintenance Notice**  
> This repository is under active development and continuous maintenance.  
> New features, fixes, and documentation updates will be released here.

| Date | Update |
|----------------------------|----------------------------|
| 2026-03-14 | Added **Robust-ChP Version 1**. |

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To maximize portability and usability, and to spare users from tedious software installation and system-level configuration, we provide a **prebuilt Docker image**, which means users do **not** need to manually install other dependencies.

### Prerequisites

Before running the pipeline, please make sure the following are available:

- **Docker**  
  Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) on Windows/macOS, or Docker Engine on Linux.

  

- **A valid FreeSurfer license**  
  FreeSurfer is required by the preprocessing workflow. Please obtain a valid `license.txt` from the [official FreeSurfer registration page](https://surfer.nmr.mgh.harvard.edu/registration.html).

- **Input MRI data**  
  This release currently supports **T1-weighted MRI** as input.

### Pull the Docker image

```sh
docker pull ggbondzzx/robust-chp:lilab-v1
```
### Run the pipeline

A generic example is shown below:
```sh
docker run --rm -it \
  --mount type=bind,src="<PATH_TO_LICENSE>/license.txt",dst=/opt/freesurfer/license.txt,readonly \
  --mount type=bind,src="<PATH_TO_INPUT_DIR>",dst=/data,readonly \
  --mount type=bind,src="<PATH_TO_OUTPUT_DIR>",dst=/out \
  ggbondzzx/robust-chp:lilab-v1 \
  run_robustchp.sh \
  --input /data/<INPUT_T1W_FILE>.nii.gz \
  --output /out \
  --gpu <GPU_ID> \
  --mode <MODEL_SCALE> \
  --modal T1w \
  --analysis
```
#### Command-Line Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `--input` | `str` | Absolute path to the input MRI inside the container. In the Docker examples above, this should usually be specified under `/data/`. |
| `--output` | `str` | Absolute path to the output directory inside the container. In the Docker examples above, this is typically `/out`. |
| `--gpu` | `str` | GPU device identifier. Use a non-negative integer such as `0` to run on a specific GPU, or use `-1` to force CPU-only execution. |
| `--mode` | `str` | Model scale used for the final segmentation stage. Supported options are `Base`, `Small`, and `Tiny`. |
| `--modal` | `str` | Input modality. The current release supports `T1w`. |
| `--fast` | `flag` | Enables a simplified fast mode that skips several upstream preprocessing and auxiliary estimation steps for quicker inference. |
| `--analysis` | `flag` | Enables post-segmentation refinement and quantitative analysis. |

#### Output Directory Structure

Robust-ChP writes intermediate segmentation outputs, and optional quantitative statistics into a structured output directory under the user-specified `--output` path.

A typical output layout is shown below:

```text
<OUTPUT_DIR>/
├── step_4_Robust-ChP/
│   ├── ChP/
│   │   ├── chp.nii.gz
│   │   └── chp4aseg.nii.gz (Follow Freesurfer's lookuptable)         
│   └── stats/
│       └── stats.json (Morphological quantitative indicators)                  
```

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Top contributors:

<a href="https://github.com/Mr-Guowang/Robust-ChP/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Mr-Guowang/Robust-ChP" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the Unlicense License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Mr-Guowang/Robust-ChP.svg?style=for-the-badge
[contributors-url]: https://github.com/Mr-Guowang/Robust-ChP/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Mr-Guowang/Robust-ChP.svg?style=for-the-badge
[forks-url]: https://github.com/Mr-Guowang/Robust-ChP/network/members
[stars-shield]: https://img.shields.io/github/stars/Mr-Guowang/Robust-ChP.svg?style=for-the-badge
[stars-url]: https://github.com/Mr-Guowang/Robust-ChP/stargazers
[issues-shield]: https://img.shields.io/github/issues/Mr-Guowang/Robust-ChP.svg?style=for-the-badge
[issues-url]: https://github.com/Mr-Guowang/Robust-ChP/issues
[license-shield]: https://img.shields.io/github/license/Mr-Guowang/Robust-ChP.svg?style=for-the-badge
[license-url]: https://github.com/Mr-Guowang/Robust-ChP/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 

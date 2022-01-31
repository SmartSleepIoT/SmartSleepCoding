
<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]




<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">SmartSleep API</h3>

  <p align="center">
    An IoT program for a smart bed device. 
    <br />
    <a href="https://docs.google.com/document/d/1VP0sfX9SmfXIrkstNCi3iEgfoAUV0fd1uXmyn17H-WI/edit"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <p>
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
  <br/>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="">Analisys document</a></li>
        <li><a href="">Interpretation and prioritization of requirements</a> </li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="">Run the project</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

"Smart Sleep" helps its users to get the perfect sleep, so they can relax and be full of energy in the morning. It's not just a product, it's a lifestyle that helps users keep up with the challenges of modern times. It's easy to use, adjusting to each user preferences and needs in real time.

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

Major frameworks/libraries used to bootstrap SmartSleep project:

* [Flask](https://flask.palletsprojects.com/en/2.0.x/)
* [Python](https://www.python.org/)

<p align="right">(<a href="#top">back to top</a>)</p>

### Analysis document
Visit it [here.](https://docs.google.com/document/d/1VP0sfX9SmfXIrkstNCi3iEgfoAUV0fd1uXmyn17H-WI/edit?usp=sharing)

### Interpretation and prioritization of requirements:
* [labels & grouping](https://github.com/SmartSleepIoT/SmartSleepCoding/issues)
* [planning poker & MoSCoW Prioritization](https://github.com/SmartSleepIoT/SmartSleepCoding/projects/1)


<!-- GETTING STARTED -->
## Getting Started

Set up SmartSleep locally:

### Prerequisites

*  Python v 3.6 or higher
* Flask
  ```sh
  pip install Flask
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/SmartSleepIoT/SmartSleepCoding.git
   ```
2. Install flask & python packages
   ```sh
   pip install -e
   ```

### Run the project
From root directory type in a terminal:
* Windows:
```shell script
start-app.sh
```
* Linux:
 ```shell script
.\start-app.sh
```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] User Account
- [x] User can set up preferences
- [x] Determine and record sleep quality
     - [x] Record breaths
     - [x] Record HeartRate
     - [x] Record Temperature
     - [X] Determine sleep stages
      
- [X] Overnight statistics
- [x] Detect and solve snoring
- [x] Alarms for waking up
- [X] Determine best intervals for wake up
- [ ] User can integrate 3rd party devices

See the [open issues](https://github.com/SmartSleepIoT/SmartSleepCoding/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



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

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Nedelcu Radu - raduN@gmail.com

Project Link: [https://github.com/SmartSleepIoT](https://github.com/SmartSleepIoT)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Resources used:

* [Flask Tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/)
* [Tailor Brands](https://studio.tailorbrands.com/brands/)
* [README Template](https://github.com/othneildrew/Best-README-Template)
* [Fitbit sensors data](https://www.fitbit.com/global/eu/home)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/SmartSleepIoT/SmartSleepCoding/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/SmartSleepIoT/SmartSleepCoding/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/SmartSleepIoT/SmartSleepCoding/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/SmartSleepIoT/SmartSleepCoding/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[product-screenshot]: images/screenshot.png




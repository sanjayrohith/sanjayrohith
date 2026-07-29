<div align="center">

<img src="./ascii.svg" width="460" alt="Animated ASCII portrait of Sanjay Rohith"/>

<img src="./stats.svg" width="620" alt="GitHub contributions in the last year"/>

[github](https://github.com/sanjayrohith)

</div>

<img src="./hd-about.svg" width="620" alt="about"/>

> I build software, learn in public, and turn ideas into useful projects.

This is my little corner of GitHub — a place for the things I am building,
experimenting with, and improving over time.

<img src="./hd-stack.svg" width="620" alt="stack"/>

<samp>add your languages, frameworks, and tools here</samp>

<img src="./hd-projects.svg" width="620" alt="projects"/>

**Featured projects**<br>
Add the repositories and short descriptions you want visitors to discover.

<img src="./hd-stats.svg" width="620" alt="stats"/>

<div align="center">

<img src="./streak.svg" width="620" alt="Current and longest contribution streak"/>

<img src="./langs.svg" width="620" alt="Top public-repository languages by bytes and repository count"/>

<img src="./year.svg" width="620" alt="Contribution activity for the last year"/>

</div>

<img src="./hd-about-this-page.svg" width="620" alt="about this page"/>

Every graphic on this page is generated inside this repository. The portrait is
made locally from my own photo by [`scripts/generate_portrait.py`](scripts/generate_portrait.py),
then drawn into `ascii.svg` as an animated character grid.

The stats graphics and section headings are drawn by a [scheduled GitHub
Action](.github/workflows/stats.yml), using the GitHub GraphQL API and the
profile repository owner. The workflow runs daily and commits only files whose
content changed.

The SVGs use SMIL animation because GitHub strips scripts from READMEs. Their
JetBrains Mono font subsets are embedded directly in the files, so the page
loads without a third-party font or statistics service.

## Create your portrait

1. Add a clear, front-facing photo that you own to `portrait/source.jpg` (or use
   any local PNG/JPEG path).
2. Run `python3 scripts/generate_portrait.py portrait/source.jpg`.
3. Commit the resulting `ascii.svg`. Your source photo stays untracked.

For the best result, use a square or portrait photo with your face centered and
an uncluttered, well-lit background.

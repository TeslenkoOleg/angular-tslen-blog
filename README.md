## T-slen Blog
This repository is a dump of my Medium blog posts. You can find the original posts [here](https://medium.com/@teslenkooleg2017).
I have written these posts to share my knowledge and experience with the community. 
I hope you will find them useful.
### Github Pages usage
```
npm i -g angular-cli-ghpages
```
you can use any github project on Github pages
```
ng build -c production --base-href "https://TeslenkoOleg.github.io/angular-me-github-pages/"
```
if you have a domain
```
ng build -c production --base-href "https://blog.t-slen.com"
```
every commit from main branch will delete CNAME so you need to add it
```
cp CNAME dist/ && ngh --dir=dist
```


# Stella's Observatory
This is my personal site, meant to handle storing my thoughts on this and that. This document here explains how the site's setup and made.

## Structure
This site relies on two main folders: Pages to contain the actual content, and Styles to contain the styling. There's also Images, which at the moment only has the background. Lastly are Markdown and .vscode, pages that aren't uploaded and instead important for making the pages.

### Pages
These are HTML files containing the actual content of the site. Pages are more or less organized how you'd navigate to them, with the exceptions of index.html and base.html. These two, which should stay at the root folder, are there for different reasons. Index has to be there for neocities to recognize it as the home page of the site, the default to head to. Base is used as a template for all other pages, containing things that would be seen in all of them such as the title and navigation.

### Styles
These are css files (or at the moment, file singular) containing how the content from Pages should look. It's generally organized by groups of rules over the same thing, with comments above sayng what the rules are over.

### Non-Uploads
In truth, the site isn't written using html (kind of). For the sake of convenience, pages are written in Markdown (kind of) in the Markdown folder and converted using build.py. The file structure in Markdown is reflected in the file structure outside of it, including with index. The build program goes as deep as possible into the folders, making any markdown files they find html at the deepest, before coming back up and doing the same. The content from the markdown files is inserted inside the main element from base.html.

.vscode isn't a very important folder, it just contains a launch.json file that tells VS Code to run build.py whenever I press the run button, even if I'm in one of the markdown files.

#### Standard Markdown
Right now, build.py supports the following:
- Paragraphs (the default for a line of markdown)
- Headings (h1 through h6)
- Links
- Images
- Block Quotes
- Italics
- Bold

#### Custom Markdown
In addition to the above, build.py supports some forms of custom markdown.

##### Line Breaks
Build.py parses the files line by line, meaning each line is its own separate element. To include multiple lines together, use \n, which will be replaced by a line break element.

##### Previews
Some pages provide previews to other pages with a link and summary. To do so, include `< X Y` in your file. X is the directory that the previews will be retrieved from, and Y is the number to retrieve (if you'd like them all, Y should be 0). For each preview, this creates a blockquote with a link to the page via its title and the first hundred or so characters of the page's paragraph content, alongside some keywords about the page, which will be explained below.

##### Tags
Each markdown page needs to have a line with --- at the bottom. This is meant to separate the main content from tags, essentially a convenient way to provide metadata. Any kind of tags can be added, but the ones currently used are Title, Date, and Keywords. 

Title is the used for the page's title element and displayed in previews. Date is used in sorting previews, with the newest being on top. Keywords are displayed below the preview, kind of like tags on social media (I named this well after I made the tagging system).

To include a tag, on the line below the three dashes, include `Name: Value`. So for the home page, it would have `Title: Home`.

## Uploading
This site makes use of the neocities cli to upload. Login on the command line, then use `neocities push --prune .`. This will upload the files here and delete the files that don't match on the site. Personally, I prefer to include --dry-run the first time to see what would happen without actually doing so.

For files that don't need to be on the site, such as the Markdown or build.py, .gitignore is used. Any names of folders or files there won't be included in the upload.
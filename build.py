from pathlib import Path
from re import sub, MULTILINE, fullmatch, finditer, search
from datetime import datetime

class Page:
	def __init__(self, path: str, content: str, details: dict):
		self.path = path
		self.content = content
		self.details = details
		self.timestamp = datetime.strptime(self.details["Timestamp"], "%m-%d-%Y")
		self.order = 0 if "Order" not in self.details.keys() else int(self.details["Order"])

		preview = "<blockquote>"
		preview += f'<strong><a href="{self.path}">{self.details["Title"]} - {self.timestamp.strftime("%b %d %y")}</a></strong>'

		first_paragraph = search("<p>(.+)</p>",self.content)
		PREVIEW_LENGTH = 500
		if(first_paragraph):
			first_content = first_paragraph.group(1)
			first_words = first_content.split(" ")
			while(len(first_content)>PREVIEW_LENGTH):
				first_words.pop()
				first_content = " ".join(first_words)
			preview+=f"<p>{first_content}</p>"

		if("Keywords" in self.details.keys()):
			keywords = self.details["Keywords"].split(", ")
			keywords = "".join(list(f"<small>{keyword}</small>" for keyword in keywords))
			preview += f'<footer class="keywords">{keywords}</footer>'

		preview += "</blockquote>"
		self.preview = preview

with open("base.html") as base_file:
	base_text = base_file.read()

def renamePath(path: Path) -> str:
	return path.as_posix().replace("Markdown/","")

pages: list[Page] = []

def getPreviews(dir: str, number: int, reverse: bool=True) -> str:
	global pages
	applicable_pages = list(page for page in pages if dir in page.path)
	applicable_pages.sort(key=lambda x: (x.timestamp, x.order), reverse=reverse)
	if(number!=0):
		applicable_pages = applicable_pages[:number]

	return "\n\n".join(list(page.preview for page in applicable_pages))

# Turns file into html
def convertFile(path: Path) -> None:
	global pages
	# List of markdown/html pairs
	tags = [
		(r"^\n", r""), # Empty Line
		(r"^--$", r"<hr />"), # Horizontal Rule
		(r"#{6} (.+)", r"<h6>\1</h6>"), # Heading 6
		(r"#{5} (.+)", r"<h5>\1</h5>"), # Heading 5
		(r"#{4} (.+)", r"<h4>\1</h4>"), # Heading 4
		(r"#{3} (.+)", r"<h3>\1</h3>"), # Heading 3
		(r"#{2} (.+)", r"<h2>\1</h2>"), # Heading 2
		(r"#{1} (.+)", r"<h1>\1</h1>"), # Heading 1
		(r"^> (.+)", r"<blockquote>\1</blockquote>"), # Blockquote
		(r'!\[([^\]]+)\]\(([^\)]+) "([^\)]+)"\)', r'<figure><img src="\2" alt="\1"/><figcaption>\3</figcaption></figure>'), # Image
		(r"(<figure>.+<\/figure>)", r'<div class="image-group">\1</div>'), # Image group
		(r"\|\|([^|]+)\|\|\(([^\)]+)\)", r"<details><summary>\2</summary>\1</details>"), # Summary
		(r"^([^<].*)", r"<p>\1</p>"), # Paragraph

		(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>'), # Links
		(r"\*{3}([^*]+)\*{3}", r"<strong><em>\1</em></strong>"), # Bold italics
		(r"\*{2}([^*]+)\*{2}", r"<strong>\1</strong>"), # Bold
		(r"\*{1}([^*]+)\*{1}", r"<em>\1</em>"), # Italics
		(r"~~([^~]+)~~", r"<s>\1</s>"), # Strikethrough
		(r"\\n", "<br>"), # Line Break
		(r"`([^`]+)`", r"<code>\1</code>") # Code Block
	]
	with open(path, "r") as file:
		content = file.read().split("---\n")
		new_content = content[0]

	for tag in tags:
		new_content = sub(tag[0], tag[1], new_content, flags=MULTILINE)
	new_content = "\t\t\t"+"\n\t\t\t".join(new_content.splitlines())
	new_content = sub("<main>\n", f"<main>\n{new_content}", base_text)

	details = {}
	for detail in content[1].split("\n"):
		tag_match = fullmatch(r"(.+?): (.+)", detail)
		details[tag_match.group(1)] = tag_match.group(2)
	new_content = sub("<title>", f"<title>{details['Title']} - Stella's Observatory", new_content)

	for feed in finditer(r"<(<?) (.+) (\d+)", new_content):
		new_content = new_content[:feed.start()] + getPreviews(feed.group(2), int(feed.group(3)), not bool(len(feed.group(1)))) + new_content[feed.end():]

	depth = path.as_posix().count("/")-1
	new_content = sub(r'(src|href)="(?!http)(.+)"', f'\\1="{"../"*depth}\\2"', new_content)

	new_path = renamePath(path).replace(".md", ".html")
	pages.append(Page(new_path, new_content, details))

	with open(new_path, "w") as new_file:
		new_file.write(new_content)

# Convert directories inside, then files
def convertDirectory(dir: str|Path) -> None:
	path = Path(dir)
	for entry in sorted(path.iterdir(), key=lambda x: x.is_file()):
		if(entry.is_dir()):
			new_path = renamePath(entry)
			if(new_path!="Pages"):
				Path(new_path).mkdir()
			convertDirectory(entry)
		elif(entry.suffix==".md"):
			convertFile(entry)

# Empty out HTML folder
for root, dirs, files in Path("Pages").walk(top_down=False):
		for name in files:
			(root / name).unlink()
		for name in dirs:
			(root / name).rmdir()

convertDirectory("Markdown")
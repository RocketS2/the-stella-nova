from re import search, fullmatch, DOTALL, finditer, sub
from os import scandir, mkdir
from shutil import rmtree
from datetime import datetime, MINYEAR

class Page:

	def __init__(self, name: str, content: str, tags: dict):
		self.name = name
		self.link = f"{self.name.replace("Markdown/","")}.html"
		self.tags = tags
		self.title = tags["Title"] if "Title" in tags.keys() else name
		self.timestamp = datetime.strptime(tags["Timestamp"], "%m-%d-%Y") if "Timestamp" in tags.keys() else datetime(year=MINYEAR, month=1, day=1)

		self.styles = tags["Styles"] if "Styles" in tags.keys() else None
		if(self.styles):
			styles_index = content.index('<link rel="stylesheet"')
			content = content[:styles_index] + f'<link rel="stylesheet" href="{self.styles}">\n\t\t' + content[styles_index:]

		self.body_class = tags["Class"] if "Class" in tags.keys() else None
		if(self.body_class):
			content = content.replace("<body>", f'<body class="{self.body_class}">')

		depth = self.name.count("/")-1
		content = sub(r'href="(?!https:\/\/)(.+)">',f'href="{"../"*depth}\\g<1>">', content)
		self.content = content.replace("<title></title>",f"<title>{self.title} - Stella's Observatory</title>")

		self.keywords = tags["Keywords"].split(", ") if "Keywords" in tags.keys() else []
		self.navigation = tags["Navigation"] if "Navigation" in tags.keys() else None

		first_paragraph = search(r"<p>(.+?)<\/p>", self.content, DOTALL)
		PREVIEW_LENGTH = 100
		first_paragraph = sub(r"(?:<.+?>)|\t|\n", "", first_paragraph.group(1)) if first_paragraph!=None else ""
		if(len(first_paragraph)<=PREVIEW_LENGTH):
			self.preview = first_paragraph
		else:
			words = first_paragraph.split(" ")
			preview_words = []
			for word in words:
				preview_words.append(word)
				if(len(" ".join(preview_words))>PREVIEW_LENGTH):
					preview_words.pop()
					break
			self.preview = " ".join(preview_words)+"..."

	def __lt__(self, other) -> bool:
		return self.timestamp<other.timestamp
		

pages: list[Page] = []

def getPages(path: str, number: int) -> list[Page]:
	found_pages = list(page for page in pages if page.name.startswith(path) and "/." not in page.name)
	
	found_pages.sort(reverse=True)

	if(number==0):
		return found_pages

	return found_pages[:number]

def getSubNav(path):
	pages_to_link = list(page for page in pages if fullmatch(f".*{path}\\/[^\\/]+",page.name))
	if(len(pages_to_link)==0):
		return ""
	links = "".join(list(f'\n{"\t"*(base_num_tabs+2)}<li><a href="{page.link}">{page.title}</a></li>' for page in pages_to_link))
	return f'\n{"\t"*base_num_tabs}<nav aria-label="{path}">\n{"\t"*(base_num_tabs+1)}<ul>{links}\n{"\t"*(base_num_tabs+1)}</ul>\n{"\t"*base_num_tabs}</nav>'

# Get base file to work from
with open("base.html") as base_file:
	base_text = base_file.read()

	base_file_body_end = search(r"\n(\t*)<\/main>", base_text)

	base_num_tabs = base_file_body_end.group(1).count("\t")+1
	base_insert_index = base_file_body_end.start(0)

	base_file_header_end = search(r"\n(\t*)<\/header>", base_text)
	base_header_insert_index = base_file_header_end.start(0)

def parseLine(path: str, line: str, num_tabs = base_num_tabs) -> str:
	"""Turns a markdown line into html"""

	if(len(line)==0):
		return line
	
	## Entire line encapsulation

	# Heading
	heading_match = fullmatch(r"(#+) (.+)", line)
	if(heading_match):
		heading_count = heading_match.group(1).count("#")
		if(heading_count>6):
			raise Exception("Only headings up to h6 supported!")
		line = f"<h{heading_count}>{heading_match.group(2)}</h{heading_count}>"

	# Block Quote
	blockquote_match = fullmatch(r"> (.+)", line, DOTALL)
	if(blockquote_match):
		line = f"<blockquote>\n{"\t"*(num_tabs+1)}{blockquote_match.group(1)}\n{"\t"*num_tabs}</blockquote>"

	# Preview
	preview_match = fullmatch(r"< (?:([^,]+?), )*(.+) (\d+)", line)
	if(preview_match):
		lines = []
		preview_match_groups = list(x for x in preview_match.groups() if x!=None)
		for subpath in preview_match_groups[:-1]:
			for page in getPages(path+subpath, int(preview_match_groups[-1])):
				keywords = f"".join(list(f"\n{"\t"*(num_tabs+2)}<small>{keyword}</small>" for keyword in page.keywords))
				lines.append(f'<blockquote>\n{"\t"*(num_tabs+1)}<strong><a href="{page.link}">{page.title}</a></strong>\n{"\t"*(num_tabs+1)}<p>\n{"\t"*(num_tabs+2)}{page.preview}\n{"\t"*(num_tabs+1)}</p>\n{"\t"*(num_tabs+1)}<footer class="keywords">{keywords}\n{"\t"*(num_tabs+1)}</footer>\n{"\t"*num_tabs}</blockquote>')
		line = f"\n{"\t"*num_tabs}".join(lines)

	# Images
	image_group_match = fullmatch(r'(!\[([^\]]+)\]\(([^\)]+?)(?: "([^\)]+)")?\))+', line)
	if(image_group_match):
		lines = []
		for image_match in finditer(r'!\[([^\]]+)\]\(([^\)]+?)(?: "([^\)]+)")?\)', line):
			lines.append(f'<figure>\n{"\t"*(num_tabs+2)}<img src="{image_match.group(2)}" alt="{image_match.group(1)}"/>{'\n'+"\t"*(num_tabs+2)+'<figcaption>'+image_match.group(3)+'</figcaption>' if image_match.group(3) else ''}\n{"\t"*(num_tabs+1)}</figure>')
		line = f'<div class="image-group">\n{"\t"*(num_tabs+1)}'+f"\n{"\t"*(num_tabs+1)}".join(lines)+f'\n{"\t"*num_tabs}</div>'

	# Spoilers
	spoiler_group_match = fullmatch(r'\|\|(.+)\|\|\((.+)\)', line)
	if(spoiler_group_match):
		line = f'<details>\n{"\t"*(num_tabs+2)}<summary>{spoiler_group_match.group(2)}</summary>\n{"\t"*(num_tabs+2)}{spoiler_group_match.group(1)}\n{"\t"*num_tabs}</details>'

	# Classes
	class_group_match = fullmatch(r'\/(.+)\/\((.+)\)', line)
	if(class_group_match):
		line = f'<p class="{class_group_match.group(2)}">\n{"\t"*(num_tabs+1)}{class_group_match.group(1)}\n{"\t"*num_tabs}</p>'

	# Paragraph (if none of the above applied)
	if(not fullmatch(r"(?:\t*<(.+).*>.+<\/\1>)|(?:<hr>)", line, DOTALL)):
		line = f"<p>\n{"\t"*(num_tabs+1)}{line}\n{"\t"*num_tabs}</p>"

	## Within line encapsulation

	# Italics and Bold
	bold_italics_matches = finditer(r"(\*+)(.+?)(\1)", line)
	for bold_italics_match in bold_italics_matches:
		replacement_text = ""
		match bold_italics_match.group(1).count("*"):

			# Italics
			case 1:
				replacement_text = f"<em>{bold_italics_match.group(2)}</em>"

			# Bold
			case 2:
				replacement_text = f"<strong>{bold_italics_match.group(2)}</strong>"

			# Both
			case 3:
				replacement_text = f"<strong><em>{bold_italics_match.group(2)}</em></strong>"
			
			case _:
				raise Exception("Only up to 3 asterisks supported!")
			
		line = line.replace(bold_italics_match.group(0), replacement_text)

	# Links
	line = sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\g<2>">\g<1></a>', line)

	line = line.replace("\\n", "<br>")

	# Code
	line = sub(r"`(.+)`", r"<code>\g<1></code>", line)

	return line

def convertMarkdownToHtml(name: str) -> None:
	"""Converts a markdown file (name.md) into an html file (name.html) using the base template"""
	path = fullmatch(r"((?:.+\/)+).+",name).group(1)
	with open(f"{name}.md") as file:
		file_lines = file.read().split("\n")
		file_split_index = file_lines.index("---")

		file_tags = {}
		for line in file_lines[file_split_index+1:]:
			tag_match = fullmatch("(.+?): (.+)", line)
			file_tags[tag_match.group(1)] = tag_match.group(2)

		file_content_lines = list("\t"*base_num_tabs+parseLine(path, line) for line in file_lines[:file_split_index])
		file_text = "\n".join(file_content_lines)
		new_text = base_text[:base_insert_index]+file_text+base_text[base_insert_index:]
		subNav = getSubNav(file_tags["Navigation"]) if "Navigation" in file_tags.keys() else ""
		new_text_with_header_subnav = new_text[:base_header_insert_index]+subNav+new_text[base_header_insert_index:]
		file_footer_start = search(r"\n(\t*)<footer>", new_text_with_header_subnav)
		file_footer_insert_index = file_footer_start.end(0)
		new_text_with_footer_subnav = new_text_with_header_subnav[:file_footer_insert_index]+subNav+new_text_with_header_subnav[file_footer_insert_index:]
		new_page = Page(name, new_text_with_footer_subnav, file_tags)
		with open(new_page.link, "w") as new_file:
			new_file.write(new_page.content)
		
		pages.append(new_page)

def convertInDirectory(path: str) -> None:
	"""Converts all the markdown files in the directory and subdirectories to html"""
	with scandir(path) as entries:
		for entry in sorted(entries, key=lambda x: x.is_file()):
			# Convert Markdown files
			if entry.name.endswith(".md"):
				convertMarkdownToHtml(f"{entry.path[:-3]}")
			# Search within folders
			elif(entry.is_dir):
				mkdir(entry.path.replace("Markdown/",""))
				convertInDirectory(entry.path)


rmtree("Pages")
convertInDirectory("Markdown")
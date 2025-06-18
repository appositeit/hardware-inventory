# Adding Screenshots to GitHub README

## Quick Guide

### 1. **Screenshot Organization**
Place screenshots in the `doc/` folder with descriptive names:
```
doc/
├── homepage.png          # Main dashboard
├── systems-list.png      # Systems listing page
├── component-detail.png  # Component details view
├── add-component.png     # Add component form
└── scan-results.png      # Scan results display
```

### 2. **Image Best Practices**
- **Format**: PNG for screenshots (better quality, transparency support)
- **Size**: Keep under 1MB each (GitHub has limits)
- **Resolution**: 1200-1600px wide is usually optimal
- **Content**: Show realistic data, not empty screens

### 3. **README Markdown Syntax**
```markdown
# Basic image
![Alt text](doc/image-name.png)

# Image with title/hover text
![Alt text](doc/image-name.png "Optional title text")

# Linked image (clickable)
[![Alt text](doc/image-name.png)](doc/image-name.png)

# HTML for more control (size, alignment)
<img src="doc/image-name.png" alt="Alt text" width="600">

# Side-by-side images
<table>
<tr>
<td><img src="doc/image1.png" alt="Image 1" width="400"></td>
<td><img src="doc/image2.png" alt="Image 2" width="400"></td>
</tr>
</table>
```

### 4. **Suggested Screenshot Sections**
Update the README with sections like:

```markdown
## Screenshots

### 🏠 Dashboard Overview
![Dashboard](doc/homepage.png)
*Main dashboard showing system and component statistics*

### 💻 Systems Management  
![Systems List](doc/systems-list.png)
*List of all scanned systems with component counts*

### 🔧 Component Details
![Component Details](doc/component-detail.png)
*Detailed view of individual components*

### ➕ Adding Components
![Add Component](doc/add-component.png)
*Form for manually adding spare components*
```

### 5. **Git Workflow for Screenshots**
```bash
# Add new screenshots
cp ~/screenshots/new-image.png doc/
git add doc/new-image.png
git add README.md  # if you updated it
git commit -m "Add: New interface screenshots"
git push
```

### 6. **Alternative: GitHub Issues/Wiki**
For extensive documentation with many images, consider:
- **GitHub Wiki**: Unlimited images, better organization
- **GitHub Pages**: Full documentation site
- **External hosting**: Imgur, your own server

### 7. **Current Status**
✅ `doc/homepage.png` - Dashboard screenshot added  
⏳ Additional screenshots needed for complete interface coverage

---

**Tip**: GitHub automatically renders images in README files, so they'll show up immediately after pushing!

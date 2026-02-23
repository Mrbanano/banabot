---
name: file-manager
description: "File operations: glob patterns, content search (grep), find files, read/write/edit files."
keywords:
  [
    file,
    glob,
    grep,
    find,
    search,
    edit,
    read,
    write,
    archivo,
    buscar,
    editar,
    leer,
    escribir,
    archivos,
  ]
metadata:
  openclaw:
    emoji: "📁"
    requires:
      bins: ["rg", "fd", "fzf"]
    install:
      - id: brew
        kind: brew
        formula: ripgrep
        bins: ["rg"]
        label: "Install ripgrep (brew)"
      - id: brew
        kind: brew
        formula: fd
        bins: ["fd"]
        label: "Install fd (brew)"
      - id: brew
        kind: brew
        formula: fzf
        bins: ["fzf"]
        label: "Install fzf (brew)"
      - id: apt
        kind: apt
        package: ripgrep
        bins: ["rg"]
        label: "Install ripgrep (apt)"
      - id: apt
        kind: apt
        package: fd-find
        bins: ["fd"]
        label: "Install fd (apt)"
      - id: apt
        kind: apt
        package: fzf
        bins: ["fzf"]
        label: "Install fzf (apt)"
---

# File Manager

File operations: search, read, write, edit using CLI tools.

## Glob (fd)

Find files by pattern:

```bash
fd "*.py"                    # All Python files in current dir
fd "*.md" --full-path docs/  # In specific path
fd --extension ts --exclude node_modules/  # Exclude dirs
fd --type d --max-depth 3     # Directories only, max 3 levels
```

## Search content (ripgrep)

Search inside files:

```bash
rg "pattern"                 # Search in current dir
rg "pattern" --type py       # Python files only
rg "pattern" -g "*.md"       # Glob pattern
rg "pattern" -C 3           # Context: 3 lines before/after
rg "pattern" -l             # Files with matches only
rg "pattern" -i             # Case insensitive
rg "pattern" --no-ignore    # Include ignored files (.gitignore)
```

## Find (fd + fzf)

Interactive file picker:

```bash
fd | fzf                     # Pick any file
fd -e md | fzf | xargs cat   # Pick and read
```

## Read files

```bash
cat file.txt                 # Full file
head -n 20 file.txt          # First 20 lines
tail -n 50 file.txt         # Last 50 lines
rg "pattern" file.txt       # Lines matching pattern
```

## Write/Edit

```bash
echo "content" > file.txt    # Overwrite
echo "content" >> file.txt   # Append

# Edit specific line with sed
sed -i '5s/old/new/' file    # Line 5

# Edit with pattern
sed -i 's/old/new/g' file    # All occurrences
```

## Tips

- Use `rg --hidden` to search hidden files
- Use `fd --exclude` to skip node_modules, .git, etc.
- Combine with `xargs` for batch operations
- Use `bat` for syntax-highlighted cat output

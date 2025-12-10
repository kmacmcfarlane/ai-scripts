# Caption Utility

A command-line utility for combining multiple caption files into a single file and splitting them back into individual files. Useful for batch editing image captions or text prompts.

## Features

- **Combine**: Merge multiple caption files into a single file for easy editing
- **Split**: Distribute a combined caption file back into individual files
- Automatic backup of existing files before overwriting
- Support for custom file extensions
- Read from stdin / write to stdout for pipeline integration

## Usage

### Combine Captions

Combine multiple caption files from a directory:
```bash
python3 caption_util.py combine --input-dir ./captions --output-file combined.txt
```

Or use short flags:
```bash
python3 caption_util.py combine -i ./captions -o combined.txt
```

Output to stdout (for piping):
```bash
python3 caption_util.py combine -i ./captions
```

Specify a custom extension:

```bash
python3 caption_util.py combine -i ./captions -e .txt
```

### Split Captions
Split a combined caption file back into individual files:
``` bash
python3 caption_util.py split --input-file combined.txt --output-dir ./captions
```

Or use short flags:
``` bash
python3 caption_util.py split -i combined.txt -d ./captions
```

Read from stdin:
``` bash
cat combined.txt | python3 caption_util.py split -i - -d ./captions
```

Specify output extension:
``` bash
python3 caption_util.py split -i combined.txt -d ./captions -e .caption
```

## Combined File Format
The combined format uses a simple structure:
``` 
filename1.caption: This is the first caption text

filename2.caption: This is another caption that can span multiple lines

filename3.caption: Short caption
```

* Each entry starts with the filename followed by a colon
* Entries are separated by blank lines
* Multi-line captions are flattened when combining

## Arguments

### Combine Command
--input-dir, -i: Directory containing caption files (default: current directory)
--output-file, -o: Output file for combined captions (default: stdout)
--extension, -e: File extension to process (default: .caption)

### Split Command
--input-file, -i: Combined caption file to read (use - for stdin) (required)
--output-dir, -d: Directory to write caption files to (default: current directory)
--extension, -e: Extension for output files (default: use filenames as-is from combined file)

### Safety Features
* Existing files are automatically backed up to backup_captions/ subdirectory before being overwritten
* Numeric suffixes are added to backup filenames if conflicts occur
* Invalid entries in combined files generate warnings but don't stop processing

### Rename Files
Rename files by changing their extension:
```bash
python3 caption_util.py rename --input-dir ./captions --input-extension .txt --output-extension .caption
```

Or use the short flag for input directory:
```bash
python3 caption_util.py rename
```

#### Rename Command Arguments

- `--input-dir, -i`: Directory containing files to rename (default: current directory)
- `--input-extension`: Extension of files to rename (default: .txt)
- `--output-extension`: New extension for renamed files (default: .caption)

#### Rename Behavior

- Finds all files with the specified input extension
- Renames them to have the output extension (preserving the base filename)
- Skips files if the target name already exists (with a warning)
- Provides feedback for each renamed file
- Shows a summary of how many files were successfully renamed



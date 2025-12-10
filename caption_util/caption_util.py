#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import shutil
from itertools import count


def normalize_extension(ext: str | None, default: str | None = None) -> str | None:
    if ext is None:
        return default
    ext = ext.strip()
    if not ext:
        return default
    if not ext.startswith("."):
        ext = "." + ext
    return ext


def combine_captions(input_dir: Path, ext: str, output_file: Path | None) -> int:
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: input directory does not exist or is not a directory: {input_dir}", file=sys.stderr)
        return 1

    files = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix == ext
    )

    if not files:
        print(
            f"Error: no files with extension '{ext}' were found in {input_dir}",
            file=sys.stderr,
        )
        return 1

    out_stream = sys.stdout
    fh = None
    try:
        if output_file is not None:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            fh = output_file.open("w", encoding="utf-8")
            out_stream = fh

        for idx, f in enumerate(files):
            try:
                content = f.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Warning: failed to read '{f}': {e}", file=sys.stderr)
                continue

            # Flatten to a single line; strip trailing whitespace
            prompt = content.strip().replace("\n", " ")

            if idx > 0:
                out_stream.write("\n")  # blank line between entries

            out_stream.write(f"{f.name}: {prompt}\n")
    finally:
        if fh is not None:
            fh.close()

    return 0


def move_to_backup(path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    target = backup_dir / path.name
    if target.exists():
        # Avoid overwriting backups; append numeric suffix
        for i in count(1):
            candidate = backup_dir / f"{path.stem}_{i}{path.suffix}"
            if not candidate.exists():
                target = candidate
                break
    shutil.move(str(path), str(target))


def parse_combined_entries(data: str):
    """
    Parse combined caption data into (filename, prompt) entries.

    Expects blocks separated by blank lines.
    Each block: "[filename]: [prompt ...]".
    """
    lines = data.splitlines()
    blocks = []
    current: list[str] = []

    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    for block in blocks:
        text = " ".join(l.strip() for l in block)
        name_part, sep, prompt_part = text.partition(":")
        if not sep:
            print(
                f"Warning: skipping malformed entry without filename/prompt separator: {text!r}",
                file=sys.stderr,
            )
            continue
        filename = name_part.strip()
        prompt = prompt_part.lstrip()
        if not filename:
            print(
                f"Warning: skipping entry with empty filename: {text!r}",
                file=sys.stderr,
            )
            continue
        yield filename, prompt


def split_captions(
    input_file: str,
    output_dir: Path,
    ext: str | None,
) -> int:
    # Allow "-" as stdin
    if input_file == "-":
        data = sys.stdin.read()
    else:
        in_path = Path(input_file)
        if not in_path.exists() or not in_path.is_file():
            print(f"Error: input file does not exist or is not a file: {in_path}", file=sys.stderr)
            return 1
        try:
            data = in_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error: failed to read input file '{in_path}': {e}", file=sys.stderr)
            return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    backup_dir = output_dir / "backup_captions"

    written_count = 0

    for raw_name, prompt in parse_combined_entries(data):
        if ext is not None:
            stem = Path(raw_name).stem
            out_name = stem + ext
        else:
            out_name = raw_name

        out_path = output_dir / out_name

        if out_path.exists():
            move_to_backup(out_path, backup_dir)

        try:
            out_path.write_text(prompt + "\n", encoding="utf-8")
            written_count += 1
        except Exception as e:
            print(f"Warning: failed to write '{out_path}': {e}", file=sys.stderr)

    if written_count == 0:
        print("Error: no files were output (no valid caption entries found).", file=sys.stderr)
        return 1

    return 0

def rename_files(
    input_dir: Path,
    input_ext: str,
    output_ext: str,
) -> int:
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: input directory does not exist or is not a directory: {input_dir}", file=sys.stderr)
        return 1

    files = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix == input_ext
    )

    if not files:
        print(
            f"Error: no files with extension '{input_ext}' were found in {input_dir}",
            file=sys.stderr,
        )
        return 1

    renamed_count = 0
    for f in files:
        new_name = f.stem + output_ext
        new_path = f.parent / new_name

        if new_path.exists():
            print(f"Warning: skipping '{f.name}' because target '{new_name}' already exists", file=sys.stderr)
            continue

        try:
            f.rename(new_path)
            renamed_count += 1
            print(f"Renamed: {f.name} -> {new_name}")
        except Exception as e:
            print(f"Warning: failed to rename '{f.name}': {e}", file=sys.stderr)

    if renamed_count == 0:
        print("Error: no files were renamed.", file=sys.stderr)
        return 1

    print(f"Successfully renamed {renamed_count} file(s).")
    return 0

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Combine and split caption files."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # combine subcommand
    p_combine = subparsers.add_parser(
        "combine",
        help="Combine individual caption files into a single stream/file.",
    )
    p_combine.add_argument(
        "--input-dir",
        "-i",
        type=str,
        default=None,
        help="Directory containing caption files (default: current working directory).",
    )
    p_combine.add_argument(
        "--output-file",
        "-o",
        type=str,
        default=None,
        help="File to write combined captions to (default: stdout). "
             "If relative, interpreted relative to --input-dir (or CWD if not set).",
    )
    p_combine.add_argument(
        "--extension",
        "-e",
        type=str,
        default=".caption",
        help="File extension to process (default: .caption).",
    )

    # split subcommand
    p_split = subparsers.add_parser(
        "split",
        help="Split a combined caption file back into individual caption files.",
    )
    p_split.add_argument(
        "--input-file",
        "-i",
        type=str,
        required=True,
        help="Combined caption file to read (use '-' to read from stdin).",
    )
    p_split.add_argument(
        "--output-dir",
        "-d",
        type=str,
        default=None,
        help="Directory to write caption files to (default: current working directory).",
    )
    p_split.add_argument(
        "--extension",
        "-e",
        type=str,
        default=None,
        help="Extension for output files (e.g. '.caption'). "
             "If omitted, filenames from the combined file are used as-is.",
    )

    # rename subcommand
    p_rename = subparsers.add_parser(
        "rename",
        help="Rename files by changing their extension.",
    )
    p_rename.add_argument(
        "--input-dir",
        "-i",
        type=str,
        default=None,
        help="Directory containing files to rename (default: current working directory).",
    )
    p_rename.add_argument(
        "--input-extension",
        type=str,
        default=".txt",
        help="Extension of files to rename (default: .txt).",
    )
    p_rename.add_argument(
        "--output-extension",
        type=str,
        default=".caption",
        help="New extension for renamed files (default: .caption).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        parser.print_usage(file=sys.stderr)
        return 1

    if args.command == "combine":
        input_dir = Path(args.input_dir) if args.input_dir is not None else Path.cwd()
        ext = normalize_extension(args.extension, default=".caption")

        output_file = None
        if args.output_file:
            out_path = Path(args.output_file)
            # Relative paths are relative to input_dir (or CWD if input_dir not given)
            base_dir = input_dir if args.input_dir is not None else Path.cwd()
            if not out_path.is_absolute():
                out_path = base_dir / out_path
            output_file = out_path

        return combine_captions(input_dir, ext, output_file)

    elif args.command == "split":
        output_dir = Path(args.output_dir) if args.output_dir is not None else Path.cwd()
        ext = normalize_extension(args.extension, default=None)
        return split_captions(args.input_file, output_dir, ext)

    elif args.command == "rename":
        input_dir = Path(args.input_dir) if args.input_dir is not None else Path.cwd()
        input_ext = normalize_extension(args.input_extension, default=".txt")
        output_ext = normalize_extension(args.output_extension, default=".caption")
        return rename_files(input_dir, input_ext, output_ext)

    else:
        print("Error: unknown command", args.command, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

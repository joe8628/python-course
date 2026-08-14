# Python Proficiency Crash Course

An assert-driven Python workbook for the experienced-but-rusty engineer. Every
exercise is a scaffold whose asserts are the spec; there are no worked solutions
anywhere, by design.

## Start here

You do not need to clone this repo. Create a folder and download the first part:

```bash
mkdir -p ~/projects/crash-course && cd ~/projects/crash-course
curl -O https://raw.githubusercontent.com/joe8628/python-course/release/part-0.md
ls part-0.md
```

`-O` is a capital letter **O**, not a zero — it is what writes the file.

Then open `part-0.md` and work it. Full instructions:
[README](python-crash-course/README.md) ·
[HOW-TO-USE](python-crash-course/HOW-TO-USE.md).

## The two branches

| Branch | What it holds | Who it's for |
|--------|---------------|--------------|
| [`release`](https://github.com/joe8628/python-course/tree/release) | the eight part files plus their two guides, flattened to the root | readers |
| `main` (here) | the same parts, plus the specs, decision records, and tooling used to author them | maintainers |

Parts reach `release` only after passing the verification gate, so nothing there
is half-finished. Corrections land on `release` too — a part fetched later is a
part fetched fresher.

import glob
import os

import click
from switch.utils.binaries import GS, QPDF
from switch.utils.files import expand_files
from switch.utils.run import file_to_temp_dir, grab_and_run, run, open_folder


@click.command(help="Generate offset plating separations from PDF files using Ghostscript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
@click.option("--pages", help="Page range to process, e.g. 1-4")
@click.option("--open", "open_out", is_flag=True, help="Open the output folder when done")
def plating(files, output, unique, copy, pages, open_out):
    for file in expand_files(*files):
        # Split PDF into single-page files using qpdf
        split_args = ("--pages", ".", pages, "--") if pages else ()
        _, split_dir = grab_and_run(
            file,
            lambda path, temp, task_id: (
                QPDF, path, *split_args, "--split-pages",
                os.path.join(temp, "%d.pdf"),
            ),
            task_name="switch_plating_split",
            unique=unique,
            copy=copy,
        )

        # Rename split files to original page numbers
        if pages:
            start = int(pages.split("-")[0])
            for split_pdf in sorted(glob.glob(os.path.join(split_dir, "*.pdf"))):
                idx = int(os.path.splitext(os.path.basename(split_pdf))[0])
                new_name = os.path.join(split_dir, "{}.pdf".format(idx + start - 1))
                os.rename(split_pdf, new_name)

        # Create output dir for separations
        out_dir = output or os.path.join(os.path.dirname(split_dir), "separations")
        os.makedirs(out_dir, exist_ok=True)

        # Run GS tiffsep1 on each single-page PDF in parallel
        page_pdfs = sorted(glob.glob(os.path.join(split_dir, "*.pdf")))
        processes = []
        for page_pdf in page_pdfs:
            stem = os.path.splitext(os.path.basename(page_pdf))[0]
            p = run((
                GS,
                "-q",
                "-dBATCH",
                "-dNOPAUSE",
                "-dSAFER",
                "-sDEVICE=tiffsep1",
                "-sCompression=g4",
                "-r2400",
                "-sOutputFile=" + os.path.join(out_dir, "{}.tif".format(stem)),
                page_pdf,
            ), wait_for_result=False)
            processes.append(p)

        for p in processes:
            p.wait()

        # Remove composite CMYK files, keep only separations
        for f in glob.glob(os.path.join(out_dir, "*.tif")):
            if "(" not in f:
                os.remove(f)

        if open_out:
            open_folder(out_dir)

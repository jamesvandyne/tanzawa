from data.files import models as file_models
from domain.files import queries as file_queries
from domain.images import images as image_ops


class UnprocessableFile(Exception): ...


def get_file(
    t_file: file_models.TFile, target_mime: str, longest_edge: int | None = None
) -> file_models.TFile | file_models.TFormattedImage:
    """
    Return the file or a processed (resized/format changed) file.
    """
    return_file = t_file
    if target_mime == t_file.mime_type and longest_edge is None:
        # They're requesting the original file so return early
        return return_file

    try:
        if file_queries.can_process_file(target_mime):
            return_file, _ = _get_or_create_processed_file(t_file, target_mime, longest_edge)
        elif longest_edge:
            return_file, _ = _get_or_create_processed_file(
                t_file, target_mime=t_file.mime_type, longest_edge=longest_edge
            )
    except UnprocessableFile:
        return t_file
    else:
        return return_file


def _get_or_create_processed_file(
    t_file: file_models.TFile, target_mime: str, longest_edge: int | None = None
) -> tuple[file_models.TFormattedImage, bool]:
    if processed_file := file_queries.get_processed_file(t_file, mime_type=target_mime, longest_edge=longest_edge):
        return processed_file, False

    width, height = image_ops.get_maybe_resized_size(t_file, longest_edge)
    if processed_file := file_queries.get_processed_file(
        t_file, mime_type=target_mime, longest_edge=max([width, height])
    ):
        return processed_file, False
    return _create_processed_file(t_file, target_mime=target_mime, longest_edge=longest_edge), True


def _create_processed_file(
    t_file: file_models.TFile,
    target_mime: str,
    longest_edge: int | None = None,
) -> file_models.TFormattedImage:
    """
    Resize and convert a t_file to a given format.

    :raises UnprocessableFile
    """
    # This should be using the same size query as we use else where
    upload_file, width, height = image_ops.convert_image_format(
        t_file, target_mime=target_mime, longest_edge=int(longest_edge) if longest_edge else None
    )
    if upload_file is None:
        raise UnprocessableFile("Unable to process file")

    formatted_file = file_models.TFormattedImage(
        file=upload_file,
        t_file=t_file,
        mime_type=target_mime,
        filename=upload_file.name,
        width=width,
        height=height,
    )
    formatted_file.save()
    return formatted_file

# mitocw-dl

Download mit opencourseware materials.

下载 [MIT OpenCourseWare](https://ocw.mit.edu/) 的课程内容，包括视频（可包含字幕）、lecture notes、recitation notes。默认下载到 `./{course_name}/`，视频和字幕放在 `videos/{lecture_name}/`，notes 放在 `notes/`。

## Usage

```bash
python download.py {course_url} {folder}
```

`folder` 可省略，默认为当前目录，无需事先创建，发现不存在会自动创建。

## TODO

- [ ] 增加下载视频和字幕后进行合并的功能。
- [ ] 增加视频超分（upscaling）功能。

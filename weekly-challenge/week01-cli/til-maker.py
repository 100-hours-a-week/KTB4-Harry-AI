import datetime
from pathlib import Path
import click

SECTIONS = [
    "핵심 배운 내용",
    "수업 중 생긴 궁금증",
    "더 알아볼 내용",
    "기타 메모",
    "오늘의 회고",
]

def get_section_content(section):
    click.echo(f"\n[{section}]")
    click.echo("내용을 입력하세요. (종료하려면 end를 입력하세요)")

    lines = []
    while True:
        # line = click.prompt("", prompt_suffix="")
        line = input()

        # 종료 문자열 유연성 추가
        if line.strip().lower() == "end":
            break
        lines.append(line)

    return "\n".join(lines)


def build_markdown(title, til_content):
    markdown = f"# {title}\n\n"

    for section, content in til_content.items():
        markdown += f"## {section}\n\n"
        markdown += f"{content}\n\n"

    return markdown


def save_markdown(markdown, today):
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "harry-til"
    output_path = output_dir / f"{today}.md"

    output_path.write_text(markdown, encoding="utf-8")

    return output_path


@click.command()
@click.option('--subject', prompt='오늘의 TIL 주제를 입력하세요 ', help='TIL 주제로 제목 생성')
def main(subject):
    today = datetime.date.today()
    title = f"[KTB] {today} TIL - {subject}"

    til_content = {}
    for section in SECTIONS:
        content = get_section_content(section)
        til_content[section] = content

    markdown = build_markdown(title, til_content)
    click.echo("\n========== 생성된 TIL ==========\n")
    click.echo(markdown)

    output_path = save_markdown(markdown, today)
    click.echo(f"TIL 파일 저장 완료: {output_path}")


if __name__ == '__main__':
    main()

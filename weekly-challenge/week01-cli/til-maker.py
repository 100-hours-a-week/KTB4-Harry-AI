# 2주차 부터는 가상환경 위에서 하는게 필수
import datetime
import click

SECTIONS = [
    "핵심 배운 내용",
    "수업 중 생긴 궁금증",
    "더 알아볼 내용",
    "기타 메모",
    "오늘의 회고",
]

@click.command()
@click.option('--subject', prompt='오늘의 TIL 주제를 입력하세요 ', help='TIL 주제로 제목 생성')
def main(subject):
    today = datetime.date.today()

    # print(f"\n오늘의 TIL 제목 : [KTB] {today} TIL - {subject}\n")
    click.echo(f"\n오늘의 TIL 제목 : [KTB] {today} TIL - {subject}\n")


if __name__ == '__main__':
    main()
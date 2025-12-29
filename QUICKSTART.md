# 🚀 빠른 시작 가이드

## 1️⃣ 설치 (완료!)

```bash
# 가상환경 활성화
venv\Scripts\activate

# 패키지가 설치되어 있습니다
```

## 2️⃣ 첫 실행

### Step 1: Topaz Gigapixel AI 실행
1. Topaz Gigapixel AI 앱을 실행하세요
2. 원하는 설정을 적용하세요:
   - 업스케일 모델 선택
   - 배율 설정 (2x, 4x, 6x 등)
   - 노이즈 제거 등 옵션

### Step 2: 스크립트 실행

**테스트용 단일 파일:**
```bash
python main.py --single "경로\이미지.jpg"
```

**폴더 전체 처리:**
```bash
# input/upscaling/ 폴더에 이미지를 넣고
python main.py

# 또는 특정 폴더 지정
python main.py --input-dir "D:\Images"
```

## 3️⃣ Quick Save vs 일반 Save

**Quick Save (기본, 권장):**
- Input 폴더에 바로 저장
- suffix 자동 추가 (예: `photo.jpg` → `photo_upscaled.jpg`)
- 빠르고 간편
- 이미 처리된 파일은 자동 제외 (무한 반복 방지)

**일반 Save:**
```bash
python main.py --input-dir "D:\Images" --use-save
```
- Output 폴더에 저장 (Topaz 앱 설정 필요)

## 4️⃣ 사용 중 주의사항

⚠️ **스크립트 실행 중에는 마우스/키보드를 사용하지 마세요!**

- 자동화가 키보드/마우스를 제어합니다
- 긴급 중단: 마우스를 화면 왼쪽 위로 이동

## 5️⃣ 대기 시간 조정 (중요!)

**"Enhancing..." 완료까지 기다리는 시간입니다!**

```bash
# 작은 이미지
python main.py --input-dir "D:\Images" --wait-time 5

# 중간 크기
python main.py --input-dir "D:\Images" --wait-time 10

# 큰 이미지 / 6x 업스케일
python main.py --input-dir "D:\Images" --wait-time 20
```

⚠️ **너무 짧으면 불완전한 이미지가 저장됩니다!**

## 🎉 완료!

처리된 이미지는 Topaz 앱에서 설정한 위치에 저장됩니다.

---

## 📝 문제 해결

### "Topaz 앱을 찾을 수 없습니다"
→ Topaz Gigapixel AI를 먼저 실행하세요

### 이미지가 안 열려요
→ 파일 경로를 확인하고, 지원하는 포맷인지 확인하세요

### 처리가 너무 빨라요
→ `--wait-time 10` 으로 대기 시간을 늘리세요


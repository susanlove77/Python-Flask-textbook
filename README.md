# Python_Flask
파이썬플라스트웹앱

로컬 환경에 가상 환경 만들기
- 파이썬에서 개발할 때에는 개발 프로젝트별로 전용 실행환경을 만들고 전환해서 사용할 수 있다.
- 임시로 만드는 개발용 실행환경을 가상환경이라고 함
- 로컬 환경에서 개발을 진행하려면 우선 가상환경(venv) 모듈을 사용해 로컬 환경에 가상환경을 작성한다.
- venv는 파이썬에 표준 탑재된 가상환경용 모듈임
- venv를 사용하면 프로젝트별로 분리된 파이선의 실행환경을 만들 수 있어 프로젝트별로 독립된 파이썬 패키지 군을 설치할 수 있다.

가상환경 설정하기
- 파워셀(실행정책설정) : PowerShell Set-ExecutionPolicy RemoteSigned CurrentUser
- 파워셀(실행정책보기) : Get-ExecutionPolicy -List
- https://learn.microsoft.com/ko-kr/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5

파워셀(venv 디렉토리생성 및 가상환경생성) : py -m venv venv -> dir
- https://heytech.tistory.com/295

파워셀(가상환경 활성화) : .\venv\Scripts\Activate.ps1
- 가상환경이 활성화 되면 프롬프트 앞쪽에 (venv)가 표시됨 (가상환경 진입)
- 가상환경 종료시 deactivate

플라스트 설치 및 가상환경 연동
- cd\
- mkdir flaskbook (디렉토리생성)
- cd flaskbook (작업디렉토리 이동)
- py -m venv venv (가상환경 생성) -> dir
- .\venv\Scripts\Activate.ps1 (가상환경 활성화)
- pip install flask (플라스크 설치)
- pip list (플라스크 의존성 패키지 확인)


- Package      Version
------------ -------
- blinker      1.9.0
- click        8.3.1 -> 8.1.3 (명령어 라인용 프레임워크, 플라스크의 커스텀 명령어 사용)
- colorama     0.4.6
- Flask        3.1.2 -> 2.2.2
- itsdangerous 2.2.0 -> 2.1.2 (안전하게 데이터를 서명해 데이터의 정합성을 확보, 세션이나 쿠키를 보호)
- Jinja2       3.1.6 -> 3.1.2 (프론트 : 기본적은 html 템플릿 엔진, 리엑트 등으로 사용해도 됨)
- MarkupSafe   3.0.3 -> 2.1.1 (인젝선 공격을 회피하기 위해 템플릿을 렌더링 할때 신뢰할 수 없는 입력을 취소함)
- pip          22.3.1 -> 22.2.2
- setuptools   65.5.0 -> 63.2.0
- Werkzeug     3.1.4 -> 2.2.2 (WSGI 툴킷으로 플라스트의 코어 : 독일어(벨저크))
- python.exe -m pip install --upgrade pip (업그레이드 pip)

플라스크 명령어
```
(venv) PS C:\flaskbook> flask

Error: Could not locate a Flask application. Use the 'flask --app' option, 'FLASK_APP' environment variable, or a 'wsgi.py' or 'app.py' file in the current directory.


Usage: flask [OPTIONS] COMMAND [ARGS]...

  A general utility script for Flask applications.

  An application to load must be given with the '--app' option, 'FLASK_APP'
  environment variable, or with a 'wsgi.py' or 'app.py' file in the current
  directory.

Options:
  -e, --env-file FILE   Load environment variables from this file, taking
                        precedence over those set by '.env' and '.flaskenv'.
                        Variables set directly in the environment take highest
                        precedence. python-dotenv must be installed.
  -A, --app IMPORT      The Flask application or factory function to load, in
                        the form 'module:name'. Module can be a dotted import
                        or file path. Name is not required if it is 'app',
                        'application', 'create_app', or 'make_app', and can be
                        'name(args)' to pass arguments.
  --debug / --no-debug  Set debug mode.
  --version             Show the Flask version.
  --help                Show this message and exit.

Commands:
  routes  Show the routes for the app. (앱의 라우팅 정보를 출력 : 경로)
  run     Run a development server. (플라스크의 내장 서버를 실행하는 명령어)
  shell   Run a shell in the app context. (플라스크 앱의 컨텍스트(실행환경)에서 파이썬 인터랙티브 셀을 사용하고 싶은 경우(디버깅, 테스트용)
```
```
(venv) PS C:\flaskbook> flask run --help
Usage: flask run [OPTIONS]

  Run a local development server.

  This server is for development purposes only. It does not provide the
  stability, security, or performance of production WSGI servers.

  The reloader and debugger are enabled by default with the '--debug' option.

Options:
  --debug / --no-debug            Set debug mode.
  -h, --host TEXT                 The interface to bind to. (호스트를 지정)
  -p, --port INTEGER              The port to bind to.      (포트를 지정)
  --cert PATH                     Specify a certificate file to use HTTPS. (https용 인증서버)
  --key FILE                      The key file to use when specifying a (https용 인증파일)
                                  certificate.
  --reload / --no-reload          Enable or disable the reloader. By default (자동 리로드)
                                  the reloader is active if debug is enabled.
  --debugger / --no-debugger      Enable or disable the debugger. By default (디버그 모드)
                                  the debugger is active if debug is enabled.
  --with-threads / --without-threads
                                  Enable or disable multithreading.
  --extra-files PATH              Extra files that trigger a reload on change.
                                  Multiple paths are separated by ';'.
  --exclude-patterns PATH         Files matching these fnmatch patterns will
                                  not trigger a reload on change. Multiple
                                  patterns are separated by ';'.
  --help                          Show this message and exit.
```
```
flask routes는 앱의 라우팅 정보를 출력한다.  
- 요청한 곳의 url과 실제 메서드(함수)를 연결하는 곳
-            Role       Endpoint Method
Endpoint Method Role
-------------------------
index    GET    /
static   GET    /static/<path:filename>

(venv) PS C:\flaskbook> flask routes --help (Endpoint Method Role)
Usage: flask routes [OPTIONS]

  Show all registered routes with endpoints and methods.

Options:
  -s, --sort [endpoint|methods|domain|rule|match]
                                  Method to sort routes by. 'match' is the
                                  order that Flask will match routes when
                                  dispatching a request.
  --all-methods                   Show HEAD and OPTIONS methods.
  --help                          Show this message and exit.
  
```
vsCode를 다운 받는다.
- https://code.visualstudio.com/docs/?dv=win64user
- extensions -> python 확장기능 설치 
```
PS C:\> cd .\flaskbook\
PS C:\flaskbook> code .
PS C:\flaskbook>


```

View에 터미널을 연다
```
https://wikidocs.net/7896
https://icedhotchoco.tistory.com/entry/PEP-8
파이썬엔 PEP(Program Enhance Proposal)이란 것이 있다.

앞 절의 "The Zen of Python"도 그 중 하나인데 코딩 방법에 대한 제안서도 있다.
그게 PEP-8이란 문서란다. "The Zen of Python"이 파이썬이 추구하는 철학에 관한 것이라면, 이 문서는 구체적인 실현 방법에 대한 것이다.

PS C:\flaskbook> .\venv\Scripts\Activate.ps1
(venv) PS C:\flaskbook> pip install flake8 black isort mypy
설치중!!
(venv) PS C:\flaskbook> pip list
Package           Version
----------------- -------
black             25.11.0 -> PEP8에 따른 작성법에 코드를 자동으로 완성한다.
blinker           1.9.0
click             8.3.1
colorama          0.4.6
flake8            7.3.0 -> PEP8에 따른 작성법의 코드인지 여부를 자동으로 체크
Flask             3.1.2
isort             7.0.0 -> import문을 PEP8에 따른 작성법으로 자동으로 정렬한다.
itsdangerous      2.2.0
Jinja2            3.1.6
librt             0.7.3
MarkupSafe        3.0.3
mccabe            0.7.0
mypy              1.19.0 -> 타입 힌트의 타입을 확인한다.
mypy_extensions   1.1.0
packaging         25.0
pathspec          0.12.1
pip               25.3
platformdirs      4.5.1
pycodestyle       2.14.0
pyflakes          3.4.0
pytokens          0.3.0
setuptools        65.5.0
typing_extensions 4.15.0
Werkzeug          3.1.4

vsCode에 flake8 활성화하기 extensions -> flake8 설치
https://fromitive.github.io/fromitive-blog/project/2023-09-20-backtest/#1-black-flake8-requirements

vsCode에 1행 최대 문자수 변경하기
Flake8 Args -> --max-line-length=88

포메터를 black으로 변경하기
Python > Formatting: Provider

https://blog.jagaldol.com/development/python-dev-env-setting-1/

파일저장시 자동 포멧 기능 활성화 
Python > Formatting On Save

isort 설정하기 extensions -> isort 설치
검색상자 : Editor: Code Actions On Save -> Edit in settings.json
{
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
		"source.organizeImports": "always"     <- 추가
	},
    "flake8.args": [
        "--max-line-length=88"
    ],
    "editor.defaultFoldingRangeProvider": "ms-python.black-formatter",
    "notebook.codeActionsOnSave": {
        "source.organizeImports": "explicit"     <- 주피터 노트북에서도 하고 싶으면 추가
    }
}

mypy 설정하기 extensions -> mypy 설치
https://github.com/ml-flaskbook/flaskbook/blob/main/.vscode/settings.json
```


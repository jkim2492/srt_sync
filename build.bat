@echo on
@REM Replace bottle.py with the latest version since the default one throws an error with --onefile
set s=%cd%
pip install -r requirements.txt
curl -A "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64)" -L "https://raw.githubusercontent.com/bottlepy/bottle/master/bottle.py" -O
copy bottle.py "%s%/.venv/Scripts/bottle.py"
copy bottle.py "%s%/.venv/Lib/site-packages/bottle.py"
del /Q bottle.py
python -c "from efd import build; build()"
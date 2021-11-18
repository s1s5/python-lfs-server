# lfs-server

```
echo "binary" > a.bin
git init
git lfs install
git lfs track a.bin
git add .gitattributes a.bin 
git ci -m "initial commit"
git clone . --bare /tmp/lfs-test-repogitory.git
git remote add origin /tmp/lfs-test-repogitory.git
git push --set-upstream origin master

git config -f .lfsconfig lfs.url https://localhost:8000/
git lfs push origin master
```

uvicorn main:app --reload

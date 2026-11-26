#!/bin/bash
# TOGLL RQ5 execution environment setup - isolated to /mnt/hdd/bocchi_hdd/togll_rq5
set -x
cd /mnt/hdd/bocchi_hdd/togll_rq5
mkdir -p env && tar xf transfer.tar -C env/ && echo TAR-OK
cd env
D4J=$PWD/payload/defects4j
GEN=$D4J/framework/lib/test_generation/generation
RT=$D4J/framework/lib/test_generation/runtime
GRA=$D4J/framework/lib/build_systems/gradle
mkdir -p "$GEN" "$RT" "$GRA"
# evosuite
cp evosuite-1.1.0.jar "$GEN"/ && cp evosuite-standalone-runtime-1.1.0.jar "$RT"/
ln -sf evosuite-1.1.0.jar "$GEN/evosuite-current.jar"
ln -sf evosuite-standalone-runtime-1.1.0.jar "$RT/evosuite-rt.jar"
# randoop
cd "$GEN" && unzip -oq $OLDPWD/randoop-4.3.3.zip && ln -sf randoop-4.3.3/randoop-all-4.3.3.jar randoop-current.jar && ln -sf randoop-4.3.3/replacecall-4.3.3.jar replacecall-current.jar && ln -sf randoop-4.3.3/covered-class-4.3.3.jar covered-class-current.jar && ln -sf randoop-4.3.3/jacocoagent.jar jacocoagent.jar; cd $OLDPWD
# major
cd "$D4J" && unzip -oq $OLDPWD/major-1.3.4_jre7.zip && cp -f major/bin/.ant major/bin/ant 2>/dev/null; chmod +x major/bin/ant 2>/dev/null; cd $OLDPWD
# gradle
cd "$GRA" && unzip -oq $OLDPWD/defects4j-gradle-dists.zip && unzip -oq $OLDPWD/defects4j-gradle-deps.zip; cd $OLDPWD
# build analyzer
cp build-analyzer-0.0.1.jar "$D4J/framework/lib/" 2>/dev/null
# jdk
mkdir -p jdk8 && tar xzf jdk8-linux-x64.tar.gz -C jdk8 --strip-components=1 && echo JDK-OK
# python venv
python3 -m venv venv && ./venv/bin/pip install -q --no-index --find-links wheels pandas joblib tqdm && echo PY-OK
# perl deps: manual build order, local lib
export PERLBASE=$PWD/perllib
mkdir -p $PERLBASE
perl_install() {
  t=$1
  d=$(tar tf "$t" | head -1 | cut -d/ -f1)
  rm -rf /tmp/pbld && mkdir -p /tmp/pbld && tar xf "$t" -C /tmp/pbld
  cd /tmp/pbld/$d
  if [ -f Makefile.PL ]; then
    perl Makefile.PL INSTALL_BASE=$PERLBASE </dev/null >/dev/null 2>&1 && make -j4 >/dev/null 2>&1 && make install >/dev/null 2>&1 && echo "PERL-OK $t" || echo "PERL-FAIL $t"
  elif [ -f Build.PL ]; then
    perl Build.PL --install_base $PERLBASE </dev/null >/dev/null 2>&1 && ./Build >/dev/null 2>&1 && ./Build install >/dev/null 2>&1 && echo "PERL-OK $t" || echo "PERL-FAIL $t"
  fi
  cd $OLDPWD
}
for t in Params-Util-1.102.tar.gz Clone-0.51.tar.gz URI-5.40.tar.gz JSON-4.11.tar.gz JSON-Parse-0.62.tar.gz DBI-1.656.tgz Text-CSV_XS-1.65.tgz Text-CSV-2.06.tar.gz SQL-Statement-1.414.tar.gz DBD-CSV-0.64.tgz; do
  perl_install "$t"
done
# env file for runs
cat > env.sh <<ENVEOF
export D4J_HOME=$D4J
export JAVA_HOME=$PWD/jdk8
export PATH=$D4J/framework/bin:$D4J/major/bin:$PWD/jdk8/bin:\$PATH
export PERL5LIB=$PERLBASE/lib/perl5:$PERLBASE/lib/perl5/x86_64-linux-gnu-thread-multi
export TZ=America/Los_Angeles
ENVEOF
source env.sh
# verification
perl -MDBI -MDBD::CSV -MJSON -MJSON::Parse -MURI -e 'print "PERL-DEPS-OK\n"' 2>&1 | tail -1
perl -c $D4J/framework/bin/run_bug_detection.pl 2>&1 | tail -2
echo SETUP-DONE

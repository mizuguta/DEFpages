#!/usr/local/bin/perl

######################################
#  ちっちゃい BBS ver 1997/11/14     #
######################################

#####################
#  ユーザー定数宣言
#####################
$BBS_DIRECTORY = '';		# server内のファイル位置
$BBS_URL = '';			# web systemでのファイル位置
$BBS_HTMLFILE = 'bbs.html';	# HTMLファイルの名前
$BBS_DATAFILE = 'bbs.data';	# データファイルの名前 
$BBS_CGIFILE  = 'bbs.cgi';	# 実行ファイルの名前	
$BBS_NAME = 'DEF? BBS';	# BBSの名前
$MAX_HTML_ARTICLE = 20;		# 1画面に表示する書き込みの数 
$WRAP_WIDTH = 80;		# 1行の文字数制限
@permitted_tag = ( 'HR', 'A-HREF', 'B', 'I', 'U', 'STRIKE', 'TT', 'SUP',
		  'SUB', 'EM', 'STRONG', 'CITE', 'CODE', 'SAMP', 'Hn',
		  'KBD', 'VAR', 'DFN'	); # 許可する HTMLタグの種類

######################
#  システム定数宣言
######################
$JISKIN = '\x1B\x28\x49';
$JISIN = '\x1B\x24[\@B]';
$JISOUT = '\x1B\x28[BJ]';
$JISIO = '((\x1B\x24\x40)|(\x1B\x24\x42)|(\x1B\x28\x42)|(\x1B\x28J))';
$JISOUT_CODE = "\x1B\x28"."B";
$JISIN_CODE  = "\x1B\x24"."B";
$VERSION = '1997/11/14 19:35';

##############
#  main関数
##############
&initials;
if( $ENV{'REQUEST_METHOD'} eq "POST" )
{
	$backlog_number = -1;
	&get_article;
}
else
{
	&get_backlog_number;

	local($html) = &make_htmlfile;
	print STDOUT "Content-type: text/html\n\n";
	print STDOUT $html;
}



####################################
#  userがいじる部分(お好きに)
#  各行の"--"の末尾には、必ず'.'(ピリオド)をつけてください
#  すべての行の末尾は、';'(セミコロン)です。
####################################

#----------------------------
#  HTMLの頭の部分を書く関数
#----------------------------
sub make_htmlheader
{
	"<HTML>\n".
	"<HEAD>\n".
	"<TITLE>$BBS_NAME</TITLE>\n".	# BBSのtitleを入れます
	"</HEAD>\n\n".
	"<BODY TEXT = \"#000000\" LINK = \"#FF0000\" VLINK = \"#FF8181\" ALINK = \"#FFFFFF\" BGCOLOR = \"#FFFFFF\">\n\n".
	"<HR>\n".
	"<center>\n".
	"<font size=+2><b>DEF?</b> BBS </font><BR>\n".
	"Bulletin Board System<BR>\n".
	"<IMG SRC=\"bbsdog.gif\" ALT=\"zobie dog\">\n".
	"</center>\n".
	"<HR>\n".

	## 入力部分です。ここはいじるのはいいですが削らないでください
	"<FORM METHOD=\"POST\" ACTION=\"$BBS_CGIFILE\">\n".
	"御芳名　　　　 <INPUT TYPE=\"text\" NAME=\"name\" SIZE=64><BR>\n".
	"メールアドレス <INPUT TYPE=\"text\" NAME=\"mail\" SIZE=64><BR>\n".
	"ページアドレス <INPUT TYPE=\"text\" NAME=\"page\" SIZE=64 VALUE=\"http://\"><BR>\n".
	"　　　　　　　 <TEXTAREA NAME=\"text\" ROWS=6 COLS=64></TEXTAREA><BR>\n".
	"HTMLタグ使用:<INPUT TYPE=\"checkbox\" NAME=\"tag\"><BR>\n".
	"<center>\n".
	"<INPUT TYPE=\"submit\" VALUE=\"書き込み\">\n".
	"<INPUT TYPE=\"reset\" VALUE=\"Cancel\"><BR>\n".
	"</center>\n".
	"</FORM>\n";

	## ここから下に、書き込みが続きます
}

#-------------------------------------
#  過去logを見る場合のHTMLの先頭番号
#-------------------------------------
sub make_htmlbacklog
{
	"<HTML>\n".
	"<HEAD>\n".
	"<TITLE>$BBS_NAME</TITLE>\n".	# BBSのtitleを入れます
	"</HEAD>\n\n".
	"<BODY TEXT = \"#000000\" LINK = \"#FF0000\" VLINK = \"#FF8181\" ALINK = \"#FFFFFF\" BGCOLOR = \"#FFFFFF\">\n\n".

	"<HR>\n".
	"<center>\n".
	"<font size=+2><b>DEF?</b> BBS </font><BR>\n".
	"Bulletin Board System<BR>\n".
	"<IMG SRC=\"bbsdog.gif\" ALT=\"zobie dog\">\n".
	"</center>\n".
	"<HR>\n".

	"<p>\n".
	"<A HREF=\"./$BBS_HTMLFILE\">最新の記事に戻る</A><P>".
	"<A HREF=\"./$BBS_CGIFILE?start=".($backlog_number-1)."\">ひとつ新しい記事を見る</A><P>\n";

	## ここから下に、書き込みが続きます
}


#---------------------------------
#  HTMLの本体部分を書く関数
#  $_maxnumber : 書き込み総数
#  $_number : 書き込み番号
#  $_text : 本文
#  $_name : 名前
#  $_mail : mail address
#  $_mailurl : mail address(URL形式)
#  $_mailurl_tag : mail address(URL形式:tag化済)
#  $_pageurl : page address(URL形式)
#  $_pageurl_tag : page address(URL形式:tag化済)
#  $_year : 西暦
#  $_month : 月(1-12)
#  $_day   : 日(1-31)
#  $_week  : 曜日(英語)
#  $_jweek : 曜日(日本語)
#  $_hour24  : 時(24時間制)
#  $_hour12  : 時(12時間制:英語)
#  $_jhour12 : 時(12時間制:日本語)
#  $_minute  : 分
#  $_second  : 秒
#----------------------------------
sub make_htmlarticle
{
	"<HR><A NAME=\"$_number\"><STRONG>［$_number］</STRONG></A>".
	"$_pageurl_tag<STRONG>$_name</STRONG></A>\n".
	" ($_mailurl_tag Mail</A> ) \n".
	"$_year/$_month/$_day/($_week)	$_hour24:$_minute:$_second\n".

	"<PRE>$_text</PRE>\n";
}

#--------------------------------
#  HTMLの終わりの部分を書く関数
#  Boolean $last: 最後のpageかどうか
#--------------------------------
sub make_htmlfooter
{
	local($last) = @_;

	(($last)? # <= さわっちゃだめ ##

		### 続きがある場合 ###
		"<P>".
		"<HR>".
		"<A HREF=\"./$BBS_CGIFILE?start=".($backlog_number+1)."\">ひとつ古い記事を見る</A><P>"

	:''). #<= さわっちゃだめ ##

	### 共通 ###
	"<HR size =3>\n".
	"back to <A HREF=\"http://homepage.mac.com/mizuguti/\">index</A>\n".
	"</BODY>\n".
        "</HTML>\n";
}
 

#-----------------------------------------------------------
#  完了を通達する
#-----------------------------------------------------------
sub show_accept
{
	"<HTML>\n".
	"<HEAD>\n".
	"<TITLE>$BBS_NAME 書き込み正常終了</TITLE>\n".
	"<HEAD>\n".

        "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"5;URL=$BBS_URL$BBS_HTMLFILE?$_maxnumber\">\n".
	"<BODY BGCOLOR=\"#ffffff\" TEXT=\"#000000\" LINK=\"#ff3500\" VLINK=\"#8b1500\" ALINK=\"#ffa500\">\n\n".
	"書き込みを受付ました。\n".
	"<HR>\n".
	"<A HREF=\"$BBS_URL$BBS_HTMLFILE?$_maxnumber\">$BBS_NAME にもどる</A>\n".
	"</BODY>\n".
	"</HTML>\n";
}
	

#---------------------
#  error時の表示
#---------------------
sub error_message
{
	"<HTML>\n".
	"<HEAD>\n".
	"<TITLE>$BBS_NAME のエラー</TITLE>\n".
	"<HEAD>\n".
	"<BODY BGCOLOR=\"#ffffff\" TEXT=\"#000000\" LINK=\"#ff3500\" VLINK=\"#8b1500\" ALINK=\"#ffa500\">\n\n".
	"<CENTER><H2>エラーです！</H2></CENTER>\n".
	"<HR><BR>".
	"$_message<BR>\n".
	"<HR><BR>\n".
	"<A HREF=\"$BBS_URL$BBS_HTMLFILE\">$BBS_NAME にもどる</A>\n".
	"</BODY>\n".
	"</HTML>\n";
}


##################################################
#  program main処理
#  ここからしたは Programer以外は触らないでね
##################################################
#---------------------------
#  書き込みを取得する関数
#---------------------------
sub get_article
{
	local($buffer);		# 読み込み用buffer
	local($message);	# 文章buffer

	### 標準入力からの読み込み ###
	read( STDIN, $buffer, $ENV{'CONTENT_LENGTH'} );
	&show_nocontentmessage	if( $buffer eq "" );	# bufferにnothing

	### データファイルへの保存 ###
	&initials;
	@article = &form2article( $buffer );				# それぞれに分割
	$article_codeset_type = &kanjitype( &mixture_article(@article) );	# 漢字codeを取得
	&article2euc( *article, $article_codeset_type );	# euc化
	&remove_magiccharacter( *article )	if( $name_flag{'tag'} eq '' );
	&article_sysinfoadd( *article );				 # 情報付与 
	&check_mailaddress( @article );
	&check_httpaddress( @article );
	if( $name_flag{'name'} eq '' || $name_flag{'text'} eq '' )
	{
	    &show_nocontentmessage;
	}
	&add_datafile( @article );	# data fileに追加する

	### HTMLの作成 ###
	&make_htmlfile; 				# html fileを作成する
	local($accept_message) = "Content-type: text/html\n\n";
	$accept_message .= &show_accept; 
	print &code2jis( $accept_message, $codeset_program );
}

sub mixture_article
{
	local(@article) = @_;
	local($i,$string);

	for( $i=0; $i<($#article+1)/3; $i++ )
	{
	$string .= $article[$i*3+2];
	}

	return $string;
}

#---------------------------------------
#  mail addressが正しい形式かcheckする
#---------------------------------------
sub check_mailaddress
{
	local(@article) = @_;
	local($matching) = '[\x21\x23-\x27\x2A\x2B\x2D\x2F-\x39\x3D\x3F\x41-\x5A\x5E-\x7F]';
	local($i);

	for( $i=0; $i<($#article+1)/3; $i++ )
	{
	  if( $article[$i*3] eq 'mail' )
	{
		$_ = $article[$i*3+2];
		if( $_ eq 'hikarumania@yahoo.co.jp'){
		  &show_errormessage("internal error occured.");
		}
		elsif( $_ eq 'zen@jcom.home.ne.jp'){
		  &show_errormessage("internal error occured.");
		}
		else {
		  return if( $_ eq '');
		  return if( /^(($matching+)\.)*$matching+@(($matching+)\.)*$matching+$/ );
		  &show_errormessage("mail addressの形式が正しくありません");
		}
	}
	}
}

sub check_httpaddress
{
	local(@article) = @_;
	local($i);

	for( $i=0; $i<($#article+1)/3; $i++ )
	{
	  if( $article[$i*3] eq 'page' ){
	    $_ = $article[$i*3+2];
	    if( $_ eq 'http://www.h5.dion.ne.jp/~hika'){
	      &show_errormessage("internal error occured.");
	    }
	    elsif( $_ eq 'http://mikeneko.kikirara.jp/pon/'){
	      &show_errormessage("internal error occured.");
	    }
	  }
	}
}


#--------------------------------------
#  field nameの使用状態フラグの初期化
#--------------------------------------
sub initials
{
	local($codesample) = "ちっちゃいＢＢＳ";

	$codeset_program = &kanjitype($codesample);
	$name_flag{'name'} = '';
	$name_flag{'codeset'} = '';
	$name_flag{'mail'} = '';
	$name_flag{'page'} = '';
	$name_flag{'date'} = '';
	$name_flag{'text'} = '';

	$* = 1;			# 複数行matchingをonにする
}


#------------------------------------------
#  formで入力されたデータを分解してしまう
#------------------------------------------
sub form2article
{
	local($_) = @_;
	local(@article);

	## 各fieldごとに切り取り ##
	s/([\x20-\x25\x27-\x7F]+)(&|$)/&form2onearticle($1,*article)/ge;

	return @article;
}
sub form2onearticle
{
	local( $_,*article ) = @_;
	local( $name, $body, $i, $line );

	($name) = /(.+)=.*/;
	($body) = /.+=(.*)/;
	$name_flag{$name} = $body  unless( $body eq "" );	# flag on

	$i = $#article;
	$article[$i+3] = &form_decode( $body, *line );
	$article[$i+2] = $line; 						# articleの行数
	$article[$i+1] = $name;
}
sub form_decode
{
	local( $string, *line ) = @_; 
	local( $i, $code, $_ );

	$string =~ s/\+/ /g;		# 空白文字
	for( $i=0; $i<length($string); $i++ )
	{
	$_ = substr($string,$i,3);
	next unless( /%[a-fA-F0-9][a-fA-F0-9]/ );

	($code) = /%([a-fA-F0-9][a-fA-F0-9])/;
	substr($string,$i,3) = pack("C", hex($code) );
	}

	$_ = $string;
	s/\r\n/\n/g;		# 改行コード修正
	s/\n\r/\n/g;		# 改行コード修正
	s/\r/\n/g;		# 改行コード修正

	$line = s/\n/\n/g;
	$line += 1;

	return $_;
}

#----------------------------------
#  <とか>を、&形式になおしてしまう
#----------------------------------
sub remove_magiccharacter
{
	local( *article ) = @_; 
	local( $i, $_ );

	for( $i=0; $i<$#article; $i+=3 )
	{
	$_ = $article[$i+2];
	s/&/\&amp;/g;
	s/</\&lt;/g;
	s/>/\&gt;/g;
	$article[$i+2] = $_;
	}
}


#------------------------------------------------------
#  漢字codeを判断する関数
#  引数は調べる文字列。返り値は 'jis'|'euc'|'sjis'
#------------------------------------------------------
sub kanjitype
{
	local( $_ ) = @_;
	local( $euc_count, $sjis_count );

	return 'jis' if /$JISIN/;
	return 'jis' if /$JISKIN/;
	return 'jis' if /\x0E[\x20-\x5F]+\x0F/;

	$euc_count = &count_euc( $_, 0 );
	$sjis_count = &count_sjis( $_, 0 );

	return 'sjis'	 if( $euc_count < 0 && $sjis_count >= 0 );
	return 'euc'	 if( $sjis_count < 0 && $euc_count >= 0 );
	if($sjis_count >= 0 && $euc_count >= 0 )
	{
	return 'euc'   if( $euc_count > $sjis_count );

	$euc_count = &count_euc( $_, 1 );
	$sjis_count = &count_sjis( $_, 1 );

	return 'euc'	 if( $sjis_count < 0 && $euc_count >= 0 );
	return 'sjis'	 if( $euc_count < 0 && $sjis_count >= 0 );

	return 'euc';
	}

	return 'jis';		# unknownのときの処理
}

#--------------------------------------
#  sjis/eucにmatchする文字数を数える
#--------------------------------------
sub count_sjis
{
	local($_,$flag) = @_;
	local( $count, $kana );

	$count = s/([\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC])//g;
	$kana  = s/[\xA1-\xDF]//g;
	$count += $kana   if( $flag );
	s/[\x0-\x7F]//g;

	$count = -1 	if( length($_) > 0 );

	return $count;
}

sub count_euc
{
	local($_,$flag) = @_;
	local( $count, $kana );

	$count = s/([\xA1-\xFE][\xA1-\xFE])//g;
	$kana  = s/(\x8E[\xA1-\xDF])//g;
	$count += $kana   if( $flag );
	s/[\x0-\x7F]//g;

	$count = -1 	if( length($_) > 0 );

	return $count;
}


#----------------------------------------
#  すべての articleを eucに変換する関数
#----------------------------------------
sub article2euc
{
	local( *article, $type) = @_; 
	local( $i, $mes );

	for( $i=0; $i<$#article; $i+=3 )
	{
	$mes = &code2jis( $article[$i+2], $type );
	$article[$i+2] = &jis2euc( $mes );
	}
}


#---------------------------------------
#  articleに、各種system情報を付加する
#---------------------------------------
sub article_sysinfoadd
{
	local( *article ) = @_; 
	local( $i );

	$i = $#article;

	$article[$i+1] = 'date';
	$article[$i+2] = 1;
	$article[$i+3] = &get_currenttime;
	$article[$i+4] = 'remote_host';
	$article[$i+5] = 1;
	$article[$i+6] = $ENV{'REMOTE_HOST'};
	$article[$i+7] = 'http_referer';
	$article[$i+8] = 1;
	$article[$i+9] = $ENV{'HTTP_REFERER'};
}
sub get_currenttime
{
	local( @ct ) = localtime(time);
	
	return "$ct[5]:".($ct[4]+1).":$ct[3]:$ct[6]:$ct[2]:$ct[1]:$ct[0]";
}


#--------------------------
# data fileに追加保存する
#--------------------------
sub add_datafile
{
	local( @article ) = @_;
	local( $i );


	### データファイルのopen ###
	open( FP, ">> $BBS_DIRECTORY$BBS_DATAFILE" ) || &show_errormessage("dataファイル作成失敗");
	flock( FP, 2 );


	### データファイルへの追加 ###
	print FP "article\t1\n".(($#article+1)/3)."\n";
	for( $i=0; $i<=$#article; $i+=3 )
	{
	print FP "$article[$i]\t$article[$i+1]\n";
	print FP "$article[$i+2]\n";
	}

	close( FP );
}

#-----------------------------------
#  datafileから、HTMLを作成する関数
#-----------------------------------
sub make_htmlfile
{
	local( $i );
	local( $cmd, $line );
	local( @article );
	local( @article_linenumber );		# 各articleの先頭行番号を格納する

	### data fileから読み込む ###
	open( FP, "$BBS_DIRECTORY$BBS_DATAFILE" ) || &show_errormessage("dataファイル読込失敗");

	### 各articleの先頭を見つける ###
	local( $article_total ) = 0;			# articleの総数
	$article_linenumber[0] = 0;
	for( $i=0; !eof(FP); $i++ )
	{
		local( $fileoffset );
		$fileoffset = tell(FP);

		$_ = <FP>;
		&command_check( $_, *cmd, *line );

		if( $cmd eq 'article' )
		{
			$article_linenumber[$article_total] = $fileoffset;
			++$article_total;
		}
	}
	$_maxnumber = $article_total;
	print STDOUT "Content-type: text/html\n\nmn,bn,at,ks:$_maxnumber,$backlog_number,$article_total,($article_codeset_type)\n"  if($name_flag{'version'} eq '41799' );

	### 表示すべき articleまで進める ###
	local( $article_count ) = 0;
	local( $article_count_in_page ) = $MAX_HTML_ARTICLE;
	local( $j );
	local( $article_top ) = $article_total - $MAX_HTML_ARTICLE;	# articleの先頭番号
	$article_top -= $MAX_HTML_ARTICLE * $backlog_number  if( $backlog_number > 0 );		# 何枚昔にさかのぼるか
	if( $article_top < 0 )
	{
	    $article_count_in_page += $article_top;
	    $article_top = 0;
	}

	seek( FP, $article_linenumber[$article_top], 0 );
	for( $i=0; !eof(FP) && $article_count_in_page >= $article_count; $i++ )
	{
		$_ = <FP>;

		&command_check( $_, *cmd, *line );
		$article[$i*3+0] = $cmd;
		$article[$i*3+1] = $line;

		for( $j=0; $j<$line; ++$j )
		{
			$article[$i*3+2] .= <FP>;
		}
		chop( $article[$i*3+2] );	### 最後についてる改行文字を削除

		if( $cmd eq 'article' )
		{
			$article_header[$article_count] = $i;
			++$article_count;
		}
	}
	$article_header[$article_count] = $i;
	close( FP );

	print STDOUT "at,i,acip,ac:$article_top,$i,$article_count_in_page,$article_count\n"  if($name_flag{'version'} eq '41799' );

	### html本体を作成する
	local( $htmlmain ) = "";
	local( $count, $k );
	$_number = 1;
	for( $i=$article_count_in_page - 1 ; $i>=0; $i-- )
	{
		$_number = $article_top + $i + 1;			# 現在の article番号
		&clear_htmlpart;
		for( $k = $article_header[$i]; $k<$article_header[$i+1]; $k++ )
		{
			&make_htmlpart( $article[$k*3+0], $article[$k*3+2] );
		}
		$htmlmain .= &make_htmlarticle;
	}

	### htmlのあたまとおしりを作成 ＆ jis化
	local( $htmlall, $htmlheader, $htmlfooter );
	local( $write_enable ) = ( $backlog_number < 0 && $name_flag{'version'} eq '' ) ? 1 : 0;
	$backlog_number = 0 if $backlog_number < 0;


	$htmlheader = ( $backlog_number == 0 ) ? &make_htmlheader : &make_htmlbacklog;
	$htmlfooter = &make_htmlfooter( $_number != 1 );

	$htmlall  = &code2jis( $htmlheader, $codeset_program );
	$htmlall .= &show_version	 if( $name_flag{'version'} != '' );
	$htmlall .= &code2jis( $htmlmain,'euc' );
	$htmlall .= &code2jis( $htmlfooter, $codeset_program );
	if( $write_enable == 1 )
	{
		open( HFP, "> $BBS_DIRECTORY$BBS_HTMLFILE" )||&show_errormessage("HTMLファイル作成失敗");
		flock( HFP, 2 );
		print HFP $htmlall;
		close( HFP );
	}

	return $htmlall;
}

sub clear_htmlpart
{
	$_mail = '';
	$_mailurl = '';
	$_mailurl_tag = '';
	$_page = '';
	$_pageurl = '';
	$_pageurl_tag = '';

	$_name = '';
	$_text = '';

	$_year	= '';
	$_month = '';
	$_day	= '';
	$_week	= '';
	$_jweek = '';

	$_hour24 = '';
	$_hour12 = '';
	$_jhour12 ='';
	$_minute = '';
	$_second = '';
}

sub make_htmlpart
{
	local( $name, $body ) = @_;
	local( @notpermitted );
	local( $_ );

	if( $name eq 'text' )
	{
	$_text = &remove_tag( $body, @permitted_tag ) ;
	$_text = ' 'x($WRAP_WIDTH).$_text	if( $WRAP_WIDTH > 0 );	# 横幅をとるための空白を表示する
	$_text =~ s/(.*)(\n|$)/&wrap_text($1,$2)/ge;
	}

	if($name eq 'mail')
	{
		$_mail = &remove_tag( $body, @notpermitted );
		$_mailurl = 'mailto:'.$_mail  if( $_mail ne '' );
		$_mailurl_tag = ($_mail eq '')?"<A NAME=\"no_mail".$_number."\">":"<A HREF=\"$_mailurl\">";
	}

	if($name eq 'page')
	{
		$_page = &remove_tag( $body, @notpermitted );
		$_pageurl = $_page  if( $_page ne '' );
		$_pageurl_tag = (($_page eq '') || ($_page eq 'http://')) ?"<A NAME=\"no_page".$_number."\">":"<A HREF=\"$_pageurl\">";
	}
	$_name = &remove_tag( $body, @notpermitted )  if($name eq 'name');

	&make_timestrings($body)  if($name eq 'date');
}
sub wrap_text
{
	local($text,$ret) = @_;
	local($i, $length, $code, $chr);
	local($count, $isfence);

	return $text.$ret	  if( $WRAP_WIDTH <= 1 );

	$length = 0;
	$isfence = 0;

	for($i=0; $i<length($text);)
	{
	$chr = substr($text, $i, 1 );
		if( $chr eq '<' )
	{
		while( substr($text,$i,1) ne '>' )
		{
		$i += 1;
		last if( $i >= length($text) );
		}
		next;
	};

	$code = unpack( 'C', $chr );
	if( $code > 0x80 )
	{
		$length += 2;
		$i += 2;

		if( $length >= $WRAP_WIDTH-1 )
		{
		substr($text, $i, 1) = "\n".substr($text,$i,1);
		$length = 0;
		$i += length("\n");
		}
	}
	else
	{
		$length += 1;
		$i += 1;

		if( $length >= $WRAP_WIDTH )
		{
		substr($text, $i, 1) = "\n".substr($text,$i,1);
		$length = 0;
		$i += length("\n");
		}
	}
	}

	return $text.$ret;
}


sub command_check
{
	local( $_, *cmd, *line ) = @_;

	$cmd = "";
	$line = "";
	($cmd) = /^(\S+)\s+\S+$/;
	($line) = /^\S+\s+(\S+)$/;
}
sub make_timestrings
{
	local( $_ ) = @_;
	local( @week ) = ( 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat' );
	local( @jweek ) = ( '日', '月', '火', '水', '木', '金', '土' );

	($_year) =	/^(\d+)/;
	$_year += 1900;
	($_month) = /^\d+:(\d+)/;
	($_day) =	/^\d+:\d+:(\d+)/;
	($_week) =	 /^\d+:\d+:\d+:(\d+)/;
	$_week = $week[$_week];
	($_jweek) =   /^\d+:\d+:\d+:(\d+)/;
	$_jweek = $jweek[$_jweek];

	($_hour24) =   /^\d+:\d+:\d+:\d+:(\d+)/;
	($_hour12) =   /^\d+:\d+:\d+:\d+:(\d+)/;
	$_jhour12 = (($_hour12 < 12)?'午前':'午後').($_hour12 % 12 );
	$_hour12 = (($_hour12 >= 12)?'AM':'PM').($_hour12 % 12 );
	($_minute) =   /^\d+:\d+:\d+:\d+:\d+:(\d+)/;
	($_second) =   /^\d+:\d+:\d+:\d+:\d+:\d+:(\d+)/;

	$_second = substr('00'.$_second, -2, 2 );
	$_minute = substr('00'.$_minute, -2, 2 );
	$_hour24 = substr('00'.$_hour24, -2, 2 );
}

#---------------------------------------------
#  日本語codeを、jisに変換する関数
#  convert_fromに、変換元のcode種類を設定する
#---------------------------------------------
sub code2jis
{
	local($_, $convert_from) = @_;
	local( $string );


	## 最初から変換すべき先が決まってるとき
	if( $convert_from eq 'jis' )
	{
	return &jis2jis( $_ );
	}
	elsif( $convert_from eq 'euc' )
	{
	return &euc2jis( $_ );
	}
	elsif( $convert_from eq 'sjis' )
	{
	return &sjis2jis( $_ );
	}
}

#----------------------------
#  sjisを jisに変換する関数
#----------------------------
sub sjis2jis
{
	local($_) = @_;

	s/(([\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC])+)/&sjis2jis_one($1)/ge;
	s/([\xA1-\xDF]+)/&sjis1bytekana($&)/ge;
	s/$JISOUT$JISIN//g; 			  # jisi/oの重なりを削除

	return	$_;
}
sub sjis2jis_one
{
	local($_) = @_;
	local($jis);

	s/../&sjis2jis_conv($&,*jis)/ge;

	return $JISIN_CODE.$jis.$JISOUT_CODE;
}
sub sjis2jis_conv
{
	local( $_, *jis ) = @_;
	local( $upper, $lower ) = unpack('CC', $_);

	$upper -= 0x40	if( $upper >= 0xE0 );
	$lower -= 0x01	if( $lower >= 0x80 ); 
	$upper = ($upper-0x81)*2 + (($lower >= 0x9E) ? 0x22 : 0x21);
	$lower = ($lower >= 0x9E) ? $lower-0x7D : $lower - 0x1F;
	$jis .= pack('CC', $upper, $lower);

	return '';
}
sub sjis1bytekana
{
	local($_) = @_;

	s/./&sjis1bytekana_one($&)/ge;

	return $JISIN_CODE.$_.$JISOUT_CODE;
}

sub sjis1bytekana_one
{
	local($_) = @_;
	local($kana2byte) = 
			"\x21\x23\x21\x56\x21\x57\x21\x22\x21\x26\x25\x72\x25\x21".
	"\x25\x23\x25\x25\x25\x27\x25\x29\x25\x63\x25\x65\x25\x67\x25\x43".
	"\x21\x3C\x25\x22\x25\x24\x25\x26\x25\x28\x25\x2A\x25\x2B\x25\x2D".
	"\x25\x2F\x25\x31\x25\x33\x25\x35\x25\x37\x25\x39\x25\x3B\x25\x3D".
	"\x25\x3F\x25\x41\x25\x44\x25\x46\x25\x48\x25\x4A\x25\x4B\x25\x4C".
	"\x25\x4D\x25\x4E\x25\x4F\x25\x52\x25\x55\x25\x58\x25\x5B\x25\x5E".
	"\x25\x5F\x25\x60\x25\x61\x25\x62\x25\x64\x25\x66\x25\x68\x25\x69".
	"\x25\x6A\x25\x6B\x25\x6C\x25\x6D\x25\x6F\x25\x73\x21\x2B\x21\x2C";
	local($code) = unpack( 'C', $_ );

	return	substr( $kana2byte, ($code-0xA1)*2, 2 );
}

#---------------------------
#  eucを jisに変換する関数
#---------------------------
sub euc2jis
{
	local($_) = @_;

	s/(\x8E[\xA1-\xDF])/&euc1bytekana($1)/ge;	  ## 1byteカナを戻す 
	s/(([\xA1-\xFE][\xA1-\xFE])+)/&euc2jis_one($1)/ge;
	s/$JISOUT$JISIN//g; 						  # jisi/oが重なったら削除

	return $_;
}
sub euc2jis_one
{
	local($_) = @_;

	tr/\xA1-\xFE/\x21-\x7E/;			  # code変換
	return $JISIN_CODE.$_.$JISOUT_CODE;   # jisi/oを付加
}
sub euc1bytekana
{
	local($_) = @_;
	local($kana2byte) = 
			"\xA1\xA3\xA1\xD6\xA1\xD7\xA1\xA2\xA1\xA6\xA5\xF2\xA5\xA1".
	"\xA5\xA3\xA5\xA5\xA5\xA7\xA5\xA9\xA5\xE3\xA5\xE5\xA5\xE7\xA5\xC3".
	"\xA1\xBC\xA5\xA2\xA5\xA4\xA5\xA6\xA5\xA8\xA5\xAA\xA5\xAB\xA5\xAD".
	"\xA5\xAF\xA5\xB1\xA5\xB3\xA5\xB5\xA5\xB7\xA5\xB9\xA5\xBB\xA5\xBD".
	"\xA5\xBF\xA5\xC1\xA5\xC4\xA5\xC6\xA5\xC8\xA5\xCA\xA5\xCB\xA5\xCC".
	"\xA5\xCD\xA5\xCE\xA5\xCF\xA5\xD2\xA5\xD5\xA5\xD8\xA5\xDB\xA5\xDE".
	"\xA5\xDF\xA5\xE0\xA5\xE1\xA5\xE2\xA5\xE4\xA5\xE6\xA5\xE8\xA5\xE9".
	"\xA5\xEA\xA5\xEB\xA5\xEC\xA5\xED\xA5\xEF\xA5\xF3\xA1\xAB\xA1\xAC";
	local( $upper, $lower ) = unpack( 'CC', $_ );

	return	substr( $kana2byte, ($lower-0xA1)*2, 2 );
}

#-------------------------------
#  jisをjisに変換する関数
#-------------------------------
sub jis2jis
{
	local($_) = @_;
	local($string);

	s/\x0E([\x20-\x5F]*)\x0F/&jis1byteMSIEkana($1)/ge;
	s/$JISKIN([\x21-\x5F]*)/&jis1bytekana($1)/ge;

	for(;;)
	{
	$string = $_;
	s/($JISIN[\x21-\x7E]*)($JISIN)/$1/g;
	last if( $string eq $_ ); 
	}

	return $_;
}
sub jis1bytekana
{
	local($_) = @_;

	s/./&jis1bytekana_one($&)/ge;

	return $JISIN_CODE.$_;
}
sub jis1bytekana_one
{
	local($_) = @_;
	local($kana2byte) = 
	"\x21\x23\x21\x56\x21\x57\x21\x22\x21\x26\x25\x72\x25\x21".
	"\x25\x23\x25\x25\x25\x27\x25\x29\x25\x63\x25\x65\x25\x67\x25\x43".
	"\x21\x3C\x25\x22\x25\x24\x25\x26\x25\x28\x25\x2A\x25\x2B\x25\x2D".
	"\x25\x2F\x25\x31\x25\x33\x25\x35\x25\x37\x25\x39\x25\x3B\x25\x3D".
	"\x25\x3F\x25\x41\x25\x44\x25\x46\x25\x48\x25\x4A\x25\x4B\x25\x4C".
	"\x25\x4D\x25\x4E\x25\x4F\x25\x52\x25\x55\x25\x58\x25\x5B\x25\x5E".
	"\x25\x5F\x25\x60\x25\x61\x25\x62\x25\x64\x25\x66\x25\x68\x25\x69".
	"\x25\x6A\x25\x6B\x25\x6C\x25\x6D\x25\x6F\x25\x73\x21\x2B\x21\x2C";
	local($code) = unpack( 'C', $_ );

	return	substr( $kana2byte, ($code-0x21)*2, 2 );
}

sub jis1byteMSIEkana
{
	local($_) = @_;

	s/./&jis1byteMSIEkana_one($&)/ge;

	return $JISIN_CODE.$_.$JISOUT_CODE;
}
sub jis1byteMSIEkana_one
{
	local($_) = @_;
	local($kana2byte) = 
	"\x21\x21\x21\x23\x21\x56\x21\x57\x21\x22\x21\x26\x25\x72\x25\x21".
	"\x25\x23\x25\x25\x25\x27\x25\x29\x25\x63\x25\x65\x25\x67\x25\x43".
	"\x21\x3C\x25\x22\x25\x24\x25\x26\x25\x28\x25\x2A\x25\x2B\x25\x2D".
	"\x25\x2F\x25\x31\x25\x33\x25\x35\x25\x37\x25\x39\x25\x3B\x25\x3D".
	"\x25\x3F\x25\x41\x25\x44\x25\x46\x25\x48\x25\x4A\x25\x4B\x25\x4C".
	"\x25\x4D\x25\x4E\x25\x4F\x25\x52\x25\x55\x25\x58\x25\x5B\x25\x5E".
	"\x25\x5F\x25\x60\x25\x61\x25\x62\x25\x64\x25\x66\x25\x68\x25\x69".
	"\x25\x6A\x25\x6B\x25\x6C\x25\x6D\x25\x6F\x25\x73\x21\x2B\x21\x2C";
	local($code) = unpack( 'C', $_ );

	return	substr( $kana2byte, ($code-0x20)*2, 2 );
}

#-----------------------------
#  jisを eucに変換する関数
#-----------------------------s
sub jis2euc
{
	local($string) = @_;
	local($i,$j,$_);

	for( $i=0; $i<length($string); $i++ )
	{
	$_ = substr($string,$i,3);
	next unless( /$JISIN/ );

	substr($string,$i,3) = '';
	for($j=$i; $j<length($string); $j++ )
	{
		$_ = substr($string,$j,3);
		next unless( /$JISOUT/ );

		substr($string,$j,3) = '';
		$_ = substr($string,$i,$j-$i);
		substr($string,$i,$j-$i) = &jis2euc_one($_);
		last;
	}
	}

	return $string;
}
sub jis2euc_one
{
	local($_) = @_;

	tr/\x21-\x7E/\xA1-\xFE/;			  # code変換

	return $_;
}


#--------------------------------
# 文字列から、tagを削除する関数
#-------------------------------- 
sub remove_tag
{
	local( $string, @permitted ) = @_;
	local( $i, $body, $result, $_ );
	local( %tag );

	&remove_remark( *string );	 ## remark不許可(default設定) ##

	for(;;)
	{
	%tag = &find_tag( *string, *i );
	last if( $tag{'top'} eq '' );

	$result = &check_tag( $tag{'top'}.' ', @permitted );
	$_ = $result;
	if( /single-.+/ )
	{	### 単一tagの場合 ###
		/.+-error/ ? substr( $string, $i, $tag{'toplength'} ) = ''
		: $i += $tag{'toplength'};
	}
	else
	{	### 対応する/tagを持つ場合 ###
		if( $tag{'end'} eq '' )
		{	### 対応するtagがないなら、削除 ###
		substr( $string, $i, $tag{'toplength'} ) = '';
		next;
		}

		if( /.+-error/ )
		{	### 禁止されているtagを削除する ###
		substr( $string, $i, $tag{'toplength'} ) = '';
		substr( $string, $i, $tag{'bodylength'} ) = '';
		substr( $string, $i, $tag{'endlength'} ) = '';
		}
		else
		{	### 許可されているtagの処理 ###
		$body = &remove_tag( $tag{'body'}, @permitted );
		substr( $string, $i+$tag{'toplength'}, $tag{'bodylength'} ) = $body;
		$i += $tag{'toplength'} + $tag{'endlength'};
		$i += length($body);
		}
	}
	}

	return $string;		## tag処理後の結果 ##
}
sub remove_remark
{
	local( *string ) = @_;
	local( $i, $j, $length );

	for(;;)
	{
	$length = length($string);
	for( $i=0; $i<$length; $i++ )
	{
		last if( substr($string,$i,4) eq '<!--' );
	}
	return	if( $i == $length );

	for( $j=$i; $j<$length; $j++ )
	{
		last if( substr($string,$j,3) eq '-->' );
	}
	if( $j == $length )
	{
		substr($string,$i,$length-$i) = '';
		return;
	}

	substr($string,$i,$j+3-$i) = '';
	}
}
#---------------------------------------------------------------------------
# 文字列から、tagを発見し、それに対応する/tagと挟まれる文字列を取得する関数
#  *i:	発見した tagの先頭部分の index
# 
#  'top'  : 先頭のtag
#  'end'  : 終わりのtag
#  'body' : tagに挟まれている部分
#  'toplength'	: 先頭tagの<から>までの長さ(length'top'と一致するとは限らない)
#  'bodylength' : bodyの長さ
#  'endlength'	: 終了tagの長さ
#  !注 : tag囲み前後は無視
#---------------------------------------------------------------------------
sub find_tag
{
	local( *string, *i ) = @_;
	local( %tag );
	local( $bodyoffset, $tagtop, $tagend );
	local( $tagoffset );

	## tagを探す ##
	$tagtop = &find_tagtop( *string, *i, *tag );
	return %tag  if( $tagtop eq '' );
	$tagoffset = $i;

	## 対応するtagを探す ##
	$i += $tag{'toplength'};
	$bodyoffset = $i;
	$tagend = &find_tagend( $string, *i, *tag );

	$tag{'bodylength'} = $i - $bodyoffset;
	$tag{'body'} = substr( $string, $bodyoffset, $tag{'bodylength'} );
	$i = $tagoffset;

	return %tag;
}
#------------------------------------------------------------------
#  先頭のtagを見つける関数(remark対応)
# *i: 発見したtagの先頭部分のindex
# 'top':  発見したtag部分。もし不完全だった場合には' 'が返される
# 'toplength' : tag部分の全体の長さ('<>'含む)
#------------------------------------------------------------------
sub find_tagtop
{
	local( *string, *i, *tag ) = @_;
	local( $j,$_, $endmark );

	## < を探す ##
	$length = length( $string );
	for( ; $i<$length; $i++ )
	{
	last if (substr($string,$i,1) eq '<');
	}
	return ''  if( $i == $length );	# もう'<'はない

	## 終了markを設定する(remark特例対応のため) ##
	$endmark = (substr($string,$i,4) eq '<!--') ? '-->' : '>';

	## > を探す ##
	for( $j = $i ; $j<$length; $j++ )
	{
	last if(substr($string,$j,length($endmark)) eq $endmark);
	}
	if( $j == $length )
	{	## 対応する'>'がなかった ##
	$tag{'toplength'} = $length - $i;
	$tag{'top'} = ' ';
	return '';
	}
	else
	{	## 対応する'>'が見つかった ##
	$tag{'toplength'} = $j+length($endmark) - $i;
	$tag{'top'} = substr($string,$i+1, $tag{'toplength'}-2);
	return $tag{'top'};
	}
}
#------------------------------------------
#  $tag{'top'}に対応するtagを発見する関数
#  $iの値は、発見したtagの'<'の位置
#------------------------------------------
sub find_tagend
{
	local( $string, *i, *tag ) = @_;
	local( $length, $j );
	local( $endtag, $_ );

	$_ = $tag{'top'};
	($endtag) = /(\S+).*/;
	$endtag = '</'.$endtag;

	## </tag  を探す
	$length = length($string);
	for(; $i<$length; $i++ )
	{
	$_ = substr($string,$i,length($endtag)+1);
	last if( /$endtag\s./i );
	last if( /$endtag>/i );
	}
	return ''  if( $i == $length );

	## とじる > を探す ##
	for( $j=$i; $j<$length; $j++ )
	{
	last if( substr($string,$j,1) eq '>' );
	}
	if( $j == $length )
	{	## 対応 fenceがない ##
	$tag{'endlength'} = $length - $i;
	$tag{'end'} = ' ';
	}
	else
	{
	$tag{'endlength'} = $j+1 - $i;
	$tag{'end'} = substr($string,$i+1,$tag{'endlength'}-2 );
	}

	return $tag{'end'};
}

#----------------------------------------------------
# tagのcheckを行って、許可/不許可などを出力する関数
#----------------------------------------------------
sub check_tag
{
	local( $tag, @permitted ) = @_;
	local($j);
	local($reply);
	local(@taglist) = (
	   'HTML:d:(^\\s*HTML\\s+$)',
	   'HEAD:d:(^\\s*HEAD\\s+$)',
	   'BODY:d:(^\\s*BODY\\s+.*$)',
	   'FRAMESET:d:(^\\s*FRAMESET\\s+.*$)',
	   'FRAME:d:(^\\s*FRAME\\s+.*$)',
	   'NOFRAMES:d:(^\\s*NOFRAMES\\s+$)',

	   'TITLE:d:(^\\s*TITLE\\s+$)',
	   'BASE-HREF:s:(^\\s*BASE\\s+HREF\\s*=\\s*\"\\S+\"\\s*$)',
	   'LINK-REV:s:(^\\s*LINK\\s+REV\\s*=\\s*\"\\S+\"\\s*$)',

	   'B:d:(^\\s*B\\s+$)',
	   'I:d:(^\\s*I\\s+$)',
	   'U:d:(^\\s*U\\s+$)',
	   'STRIKE:d:(^\\s*STRIKE\\s+$)',
	   'TT:d:(^\\s*TT\\s+$)',
	   'SUP:d:(^\\s*SUP\\s+$)',
	   'SUB:d:(^\\s*SUB\\s+$)',
	   'BIG:d:(^\\s*BIG\\s+$)',
	   'SMALL:d:(^\\s*SMALL\\s+$)',
	   'BLINK:d:(^\\s*BLINK\\s+$)',

	   'EM:d:(^\\s*EM\\s+$)',
	   'STRONG:d:(^\\s*STRONG\\s+$)',
	   'CITE:d:(^\\s*CITE\\s+$)',
	   'CODE:d:(^\\s*CODE\\s+$)',
	   'SAMP:d:(^\\s*SAMP\\s+$)',
	   'KBD:d:(^\\s*KBD\\s+$)',
	   'VAR:d:(^\\s*VAR\\s+$)',
	   'DFN:d:(^\\s*DFN\\s+$)',

	   'FONT:d:(^\\s*FONT\\s+.*$)',
	   'BASEFONT:s:(^\\s*BASEFONT\\s+SIZE\\s*=\\s*\\S+\\s*$)',

	   'Hn:d:(^\\s*H[123456]\\s+$)',
	   'H1:d:(^\\s*H1\\s+$)',
	   'H2:d:(^\\s*H2\\s+$)',
	   'H3:d:(^\\s*H3\\s+$)',
	   'H4:d:(^\\s*H4\\s+$)',
	   'H5:d:(^\\s*H5\\s+$)',
	   'H6:d:(^\\s*H6\\s+$)',

	   'P:s:(^\\s*P\\s+$)',
	   'P-ALIGN:d:(^\\s*P\\s+ALIGN\\s*=\\s*\\w+\\s*$)',

	   'A-HREF:d:(^\\s*A\\s+HREF\\s*=\\s*\"\\S+\"\\s*$)',
	   'A-NAME:d:(^\\s*A\\s+NAME\\s*=\\s*\"\\S+\"\\s*$)',
	   'SCRIPT:d:(^\\s*SCRIPT\\s+.*$)',
	   'PRE:d:(^\\s*PRE\\s+$)',
	   'BLOCKQUOTE:d:(^\\s*BLOCKQUOTE\\s+$)',

	   'HR:s:(^\\s*HR\\s+.*)',
	   'BR:s:(^\\s*BR\\s+.*)',
	   'NOBR:d:(^\\s*NOBR\\s+$)',

	   'IMG-SRC:s:(^\\s*IMG\\s+SRC\\s*=\\s*\"\\S+\"\\s+.*$)',
	   'CAPTION:d:(^\\s*CAPTION\\s+.*$)',

	   'UL:d:(^\\s*UL\\s+$)',
	   'OL:d:(^\\s*OL\\s+.*$)',
	   'DL:d:(^\\s*DL\\s+.*$)',
	   'MENU:d:(^\\s*MENU\\s+$)',
	   'DIR:d:(^\\s*DIR\\s+$)',
	   'LI:d:(^\\s*LI\\s+.*$)',
	   'DT:s:(^\\s*UL\\s+$)',
	   'DD:s:(^\\s*UL\\s+$)',

	   'TABLE:d:(^\\s*TABLE\\s+.*$)',
	   'TR:d:(^\\s*TR\\s+.*$)',
	   'TH:d:(^\\s*TH\\s+.*$)',
	   'TD:d:(^\\s*TD\\s+.*$)',

	   'FORM:d:(^\\s*FORM\\s+.*$)',
	);

	for( $j=0; $j<=$#taglist; $j++ )
	{
	$_ = $taglist[$j];
	/^((-|\w)+):(s|d):(.+)$/;

	$type = $1;
	$mode = $3;
	$match = $4;
	$_ = $tag;

	if( /$match/i )
	{
		### tag種類判別できたので、それらに対する処理を行う ###
		$reply = ($mode eq 's') ? 'single-' : 'double-';
		$reply .= &check_tag_ispermitted($type, @permitted ) ? 'ok' : 'error';
		return $reply;
	}
	}	

	return 'unknown-error';
}
#------------------------------------------------
#  引数のtagが、許可されているかどうか調べる関数
#------------------------------------------------
sub check_tag_ispermitted
{
	local( $type, @permitted ) = @_;
	local($i);

	for( $i=0; $i<=$#permitted; $i++ )
	{
	return 1  if( $type eq $permitted[$i]);
	}

	return	0;
}

#------------------------------
#  error messageを表示する関数
#------------------------------
sub show_errormessage
{
    ($_message) = @_;

    print STDOUT "Content-type: text/html\n\n";
    print STDOUT &error_message;
    exit 0;
}

#--------------------------------
# contentsがない旨を説明する関数
#--------------------------------
sub show_nocontentmessage
{
    &show_errormessage('名前と本文は省略できません。');
}

#---------------------------------------
# 何番目の過去logを見るかを取得する関数
# 過去logを見ない場合は、-1を返す
#---------------------------------------
sub get_backlog_number
{
    local( @article );
    local( $i );

    $backlog_number = -1;
    return	 if( $ENV{'QUERY_STRING'} eq '' );

    @article = &form2article( $ENV{'QUERY_STRING'} );
    for( $i=0; $i<=$#article; $i+= 3 )
    {
	if( $article[$i] eq 'start' )
	{
	    $backlog_number = $article[$i+2];
	    return;
	}
    }
}

#------------------------------
#  versionを表示する関数
#------------------------------
sub  show_version
{
	'<HR><CENTER>'.
	$VERSION.
	'</CENTER><HR>';	
}

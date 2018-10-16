/* jQuery jNotifica Plugin v3 (minified) - http://jnotifica.lenonmarcel.com.br/
Copyright 2009, 2010 Lenon Marcel
Dual licensed under the MIT and GPL licenses.
http://www.opensource.org/licenses/mit-license.php
http://www.gnu.org/licenses/gpl.html */
(function($){var
IE6=$.browser.msie&&/MSIE 6.0/.test(navigator.userAgent),Timer,IE6FIX;$.jnotifica_defaults={margin:0,position:'top',width:'all',align:'center',padding:25,background:'#000',zIndex:100,color:'#fff',opacity:0.8,cursor:'pointer',msgCss:{fontSize:'15px',fontFamily:'Arial, sans-serif',textAlign:'left'},effect:'slide',speed:500,timeout:5000,clickClose:true,close:{text:'[CLOSE]',css:{color:'#fff',fontSize:'10px',position:'absolute',top:5,right:10,cursor:'pointer'}},onShow:function(main){},onClose:function(){},classes:''}
function close(obj){var
Obj=$(obj),onClose=Obj.data('onClose'),call=function(){remove(Obj);if($.isFunction(onClose))
onClose();},spd=Obj.data('speed');switch(Obj.data('effect')){case'none':Obj.hide('',call);case'fade':Obj.fadeOut(spd,call);default:Obj.slideUp(spd,call);}}
function remove(obj){clearInterval(IE6FIX);clearTimeout(Timer);$(obj).find('div').unbind('click');$(obj).stop().remove();}
function ie6TopFix(){var element=document.getElementById('jnotifica_main');if(element){element.style.top=parseInt(document.documentElement.scrollTop)+'px';}}
function ie6BottomFix(){var element=document.getElementById('jnotifica_main');if(element){element.style.top=parseInt(document.documentElement.scrollTop+document.documentElement.clientHeight-element.offsetHeight)+'px';}}
function show(msg,opt){var
Main=$('<div id="jnotifica_main" class="jnotifica_main"/>').css({position:IE6?'absolute':'fixed',overflow:'hidden',zIndex:opt.zIndex,width:'100%',left:0}).addClass(opt.classes).hide(),Spc=$('<div class="jnotifica_spc"/>').css('padding',opt.margin),Cont=$('<div class="jnotifica_cont"/>').css({position:'relative',cursor:opt.cursor}),Bg=$('<div class="jnotifica_bg"/>').css({position:'absolute',height:'100%',top:0,left:0,width:'100%',background:opt.background,zIndex:opt.zIndex+1,opacity:opt.opacity})
Msg=$('<div class="jnotifica_msg"/>').css({position:'relative',zIndex:opt.zIndex+2,color:opt.color,padding:opt.padding}).css(opt.msgCss).html(msg);if(opt.position=='bottom')
Main.css('bottom',0)
else
Main.css('top',0);if(IE6){Bg.css('height','1000px');if(opt.position=='bottom'){Main.css('bottom','auto');IE6FIX=setInterval(function(){ie6BottomFix()},50);}else{IE6FIX=setInterval(function(){ie6TopFix()},50);}}
if(opt.width!='all'){Spc.css('width',parseInt(opt.width));if(opt.align=='left')
Spc.css('float','left')
else if(opt.align=='right')
Spc.css('float','right')
else
Spc.css({marginLeft:'auto',marginRight:'auto'})}
if(opt.close!==false){Cont.append($('<div class="jnotifica_close"/>').css(opt.close.css).css('zIndex',opt.zIndex+4).html(opt.close.text).click(function(){close(Main)}))}
$('body').append(Main.append(Spc.append(Cont.append(Bg).append(Msg))));var start=function(){if(opt.timeout>0)
Timer=setTimeout(function(){close(Main);},opt.timeout);}
switch(opt.effect){case'none':Main.show('',start);case'fade':Main.fadeIn(opt.speed,start);default:Main.slideDown(opt.speed,start);}
if(opt.clickClose)
Cont.click(function(){close(Main)});Main.data({effect:opt.effect,speed:opt.speed,onClose:opt.onClose});if($.isFunction(opt.onShow))
opt.onShow(Main);}
$.jnotifica=$.jN=function(msg,opt){msg=msg?msg:'Hello';opt=opt?opt:{};var opts=$.extend(true,{},$.jnotifica_defaults,opt);remove($('#jnotifica_main'));show(msg,opts);}
$.fn.jnotifica=$.fn.jN=function(options){return $.jN($(this).html(),options);}
$.jnotifica.close=function(){close($('#jnotifica_main'));}
$.jnotifica.version='v3';})(jQuery);
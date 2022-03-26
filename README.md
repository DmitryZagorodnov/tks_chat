# Simple TCP Chat
## Использование
### Список команд
* !LOGIN \<nickname> - осуществляет вход на сервер под именем \<nickname>. Все, что идет после разделительного пробела,
будет считаться именем пользователя
* !DISCONNECT - осуществляет выход с сервера
* !ATTACH \<file> - осуществляет отправку файла под именем \<file>. Имя файла должно включать в себя расширение. Для 
отправки файл должен находиться в одной директории с клиентом  

### Workflow
После запуска клиента пользователь будет уведомлен о необходимости войти на сервер (команда !LOGIN). При неправильной 
попытке логина пользователь будет уведомлен о необходимости перезапустить клиент. После входа пользователь может 
отправлять свои сообщения, получать чужие. Помимо обычных сообщений, пользователь может отправлять файлы (команда 
!ATTACH). При успешной отправке, пользователь будет уведомлен о том, что его файл был успешно доставлен. При отправке 
файла другим пользователем, в консоли появится сообщение о том, что вы получили файл \<file_name> от пользователя 
\<nickname>. При желании завершить общение, пользователю необходимо использовать команду !DISCONNECT, после чего он
получит уведомление об его отключении от сервера


## Описание протокола:
Для связи сервера с клиентом используются сокеты. При запуске клиента, между ним и сервером устанавливается TCP 
соединение.  
Перед отправкой сообщения сначала определяется его длина, которая будет записана в поле HEADER. Длина 
HEADER'а - 10 байт, при меньшей реальной длине он дополняется пробелами. Соответственно, может быть отправлено сообщение длиной до 999999999 байт включительно.  
Сначала посылается HEADER, получатель считывает 10 байт заголовка, затем декодирует его, определяя длину сообщения, 
следующего за ним. Затем он считывает ровно то количество байт, которое было указано в HEADER'е. Таким образом, 
структура передаваемого атомарного сообщения:  
| HEADER | message_body |  
|:--------:|:--------------:|  
|10 bytes|From 0 to 9999999999 bytes*|  

*in encoded form 

## Отправка сообщений
Когда пользователь вводит сообщение в консоль и нажимает клавишу ввода, на сервер отправляется сразу несколько атомарных
сообщений. Первым отправляется тип сообщения, какие сообщения будут отправлены следующими - зависит от него.
### Типы сообщений
* usual - тип, соответствующий обычному сообщению
* service - служебное сообщение (сообщение, содержащее команду)
* file - передаваемое сообщение является файлом
### Сообщения, отправляемые после типа
Если тип сообщения - usual:
* Тело сообщения

Если тип сообщения - file:
* Имя файла
* Содержимое файла

Если тип сообщения - service и это сообщение - команда логина:
* Сообщение о логине
* \<nickname>

Если тип сообщение - service и это сообщение - команда дисконнекта:
* Сообщение о дисконнекте

### Сервисные сообщения

* DISCONNECT_MESSAGE = "!DISCONNECT"
* LOGIN_MESSAGE = "!LOGIN"

Необходимы для того, чтобы при желании пользователь мог изменить соответствующие команды. При вводе им сообщения 
осуществляется проверка, не начинается ли оно с одной из команд, если начинается - на сервер отправляется 
соответствующая команда

## Получение сообщений от сервера

После получения цельного сообщения (типа и последующих атомарных сообщений) от одного из клиентов сервер осуществляет 
рассылку для всех пользователей, находящихся онлайн. Типы сообщений сервера аналогичны типам сообщений клиента.
Немного отличаются лишь последующие типу атомарные сообщения.  
Если тип сообщения - file:
* Имя файла
* Содержимое файла

Если тип сообщения - usual:
* Nickname автора сообщения
* Тело сообщения

Если тип сообщения - service:
* Тело сообщения

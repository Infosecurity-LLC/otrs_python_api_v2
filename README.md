Библиотека для взаимодействия с API OTRS.

В soc 2.0 предполагается использовать многопроцессорность в связи с тем, что Cortex каждый раз запускает
новый инстанс класса OTRS.

В условиях многопроцессорности важно использовать одну сессию, а не создавать каждый раз новую. Для этого подготовлена
работа с кэш файлом сессии. При этом механизм межпроцессорного доступа к файлу не реализован.
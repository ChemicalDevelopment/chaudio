
add_library(chplug SHARED chplug.c ast.c lex.c parser.c)

install (TARGETS chplug DESTINATION lib/)


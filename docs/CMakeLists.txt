find_program(MAKEINFO_EXECUTABLE makeinfo)

set(RESOURCES ../docs)
#set(RESOURCES https://github.com/ChemicalDevelopment/chaudio/raw/master/docs)

configure_file (
  "./chaudio.texi.in"
  "${PROJECT_BINARY_DIR}/docs/chaudio.texi"
)

configure_file (
  "./samplemajor.png"
  "${PROJECT_BINARY_DIR}/docs/samplemajor.png"
  COPYONLY
)

set(info_in ${CMAKE_CURRENT_BINARY_DIR}/chaudio.texi)
set(html_out ${CMAKE_CURRENT_BINARY_DIR}/index.html)
#set(html_out ${CMAKE_SOURCE_DIR}/docs/index.html)

# && sed -i -e "s/\.\.\//\.\//g" ${html_out}

add_custom_command(OUTPUT ${html_out}
  COMMAND ${MAKEINFO_EXECUTABLE} --no-split --fill-column=40 --html -o ${html_out} ${info_in}
  DEPENDS ${info_in}
  COMMENT "Creating HTML directory ${html_out}"
  VERBATIM)

add_custom_target(info ALL DEPENDS ${html_out})

"""
Testcase to build U-Boot
------------------------
"""
import typing
import tbot
from tbot import tc


@tbot.testcase
def just_uboot_build(tb: tbot.TBot) -> None:
    """
    Build U-Boot in the currently existing (possibly dirty) U-Boot tree.
    """
    uboot_dir = tb.call("uboot_checkout", clean=False)
    toolchain = tb.call("toolchain_get")
    tb.call("uboot_build", builddir=uboot_dir, toolchain=toolchain)


@tbot.testcase
def uboot_build(
    tb: tbot.TBot,
    *,
    builddir: tc.UBootRepository,
    toolchain: tc.Toolchain,
    defconfig: typing.Optional[str] = None,
    do_compile: bool = True,
) -> None:
    """
    Build U-Boot

    :param UBootRepository builddir: Where to build U-Boot
    :param Toolchain toolchain: Which toolchain to use
    :param str defconfig: What U-Boot defconfig to use, defaults to ``tb.config["uboot.defconfig"]``
    :param bool do_compile: Whether we should actually run ``make`` or skip it
    """

    defconfig = defconfig or tb.config["uboot.defconfig"]

    tbot.log.doc(
        f"""
We are using the `{toolchain.name}` toolchain and will compile \
U-Boot using the `{defconfig}` defconfig.
"""
    )

    tbot.log.doc("\n### Setting up the toolchain ###\n")

    @tb.call_then("toolchain_env", toolchain=toolchain)
    def build(tb: tbot.TBot) -> None:  # pylint: disable=unused-variable
        """ The actual build """
        tbot.log.doc(
            """
### The build process ###
Prepare the buildprocess by moving into the build directory and executing the following commands:
"""
        )
        tbot.log.debug(f"Using '{defconfig}'")
        tb.shell.exec0(f"cd {builddir}")
        tb.shell.exec0(f"make mrproper", log_show_stdout=False)
        tb.shell.exec0(f"make {defconfig}", log_show_stdout=False)

        def compile(
            tb: tbot.TBot
        ) -> None:  # pylint: disable=redefined-builtin, unused-variable
            """ The actual compilation process """
            tbot.log.doc("Start the compilation using\n")
            tb.shell.exec0(f"make -j4 all")

        if do_compile:
            tb.call(compile)

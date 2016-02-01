"""A MultiKernelManager for use in the notebook webserver

- raises HTTPErrors
- creates REST API models
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import os

from IPython.html.services.kernels.kernelmanager import MappingKernelManager
from IPython.kernel.ioloop.manager import IOLoopKernelManager

#-----------------------------------------------------------------------------
class ExistingIOLoopKernelManager(IOLoopKernelManager):

    def start_kernel(self, **kw):
        """Connect to an existing kernel.
        """

        self.connection_file = '/home/jcfr/.ipython/profile_default/security/kernel-1234.json'
        self.load_connection_file()

        self.kernel = True

        self._connect_control_socket()

    def request_shutdown(self, restart=False):
        """Send a shutdown request via control channel
        """
        pass

    def shutdown_kernel(self, now=False, restart=False):
        """Attempts to the stop the kernel process cleanly.
        """
        self.cleanup(connection_file=False)

    def restart_kernel(self, **kw):
        """Restarts a kernel with the arguments that were used to launch it.
        """
        raise RuntimeError("Cannot restart the kernel. ")

    @property
    def has_kernel(self):
        """Has a kernel been started that we are managing."""
        return self.kernel is not None

    def interrupt_kernel(self):
        """Interrupts the kernel by sending it a signal.
        """
        raise RuntimeError("Cannot interrupt kernel.")

    def signal_kernel(self, signum):
        """Sends a signal to the kernel.
        """
        raise RuntimeError("Cannot signal kernel.")

    def is_alive(self):
        """Is the kernel process still running?"""
        return self.has_kernel()


#-----------------------------------------------------------------------------
class ExistingMappingKernelManager(MappingKernelManager):
    """A KernelManager that handles notebook mapping and HTTP error handling"""

    def _kernel_manager_class_default(self):
        return "existingkernel.managers.ExistingIOLoopKernelManager"


    #-------------------------------------------------------------------------
    # Methods for managing kernels and sessions
    #-------------------------------------------------------------------------

    def start_kernel(self, path=None, kernel_name='python', **kwargs):
        """Connect to an existing kernel.

        Parameters
        ----------
        path : API path
            The API path (unicode, '/' delimited) for the cwd.
            Will be transformed to an OS path relative to root_dir.
        kernel_name : str
            The name identifying which kernel spec to launch. This is ignored if
            an existing kernel is returned, but it may be checked in the future.

        To silence the kernel's stdout/stderr, call this using::

            km.start_kernel(stdout=PIPE, stderr=PIPE)

        """
        print("*"*80)
        # kernel_id is expected to match the regular expression 'kernel_id_regex' (\w+-\w+-\w+-\w+-\w+)
        # defined in IPython.html.services.kernels.handlers
        kernel_id = "0000-1111-2222-3333-4444"
        if kernel_id in self:
            self._check_kernel_id(kernel_id)
            self.log.info("Using existing kernel: %s" % kernel_id)
            return kernel_id

        if kernel_name is None:
            kernel_name = self.default_kernel_name
        # kernel_manager_factory is the constructor for the KernelManager
        # subclass we are using. It can be configured as any Configurable,
        # including things like its transport and ip.
        km = self.kernel_manager_factory(connection_file=os.path.join(
                    self.connection_dir, "kernel-%s.json" % kernel_id),
                    parent=self, autorestart=True, log=self.log, kernel_name=kernel_name,
        )

        # FIXME: remove special treatment of IPython kernels
        if km.ipython_kernel:
            kwargs.setdefault('extra_arguments', self.ipython_kernel_argv)
        km.start_kernel(**kwargs)
        self._kernels[kernel_id] = km
        return kernel_id

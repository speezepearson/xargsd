import asyncio

async def serve_gui(command, unique, socket_file, queue):
    import bridge

    g_queue = bridge.List()

    gui = bridge.GUI(bridge.List([
        bridge.Text(f'Command: {command}'),
        bridge.Text(f'Socket file: {socket_file.resolve()}'),
        bridge.Text(f'Unique: {unique}'),
        g_queue,
    ]))

    async def keep_g_queue_updated():
        while True:
            #print('waiting for change...')
            await queue.wait_for_change()
            #print('queue changed!')
            g_queue[:] = [bridge.Text(s) for s in queue]
            #print('GUI queue:', g_queue)

    return asyncio.gather(
        keep_g_queue_updated(),
        bridge.serve_async(gui),
    )

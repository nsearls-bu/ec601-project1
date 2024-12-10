const kafka = require('./kafka')
const consumer = kafka.consumer({
  groupId: 'node-consumer'
})

const main = async () => {
    await consumer.connect()
    await consumer.subscribe({
        // hardcoded for now
        topics: ['myserver.public.inventory', 'myserver.public.orders', 'myserver.public.users'],
        fromBeginning: true,
    })

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            const value = JSON.parse(message.value);
            if (value) {
              const payload = value.payload;
              if (payload.before === null && payload.after) {
                console.log('added', payload.after, `to ${payload.source.schema}.${payload.source.table}`);
              } else if (payload.after === null && payload.before) {
                console.log('deleted', payload.before, `from ${payload.source.schema}.${payload.source.table}`);
              }
            }
            console.log('\n');
        }
    })
}

main().catch(async error => {
  try {
    await consumer.disconnect()
  } catch (e) {
    console.error('Failed to gracefully disconnect consumer', e)
  }
  process.exit(1)
})

import { headers } from 'next/headers';
import { App } from '@/components/app/app';
import { getAppConfig } from '@/lib/utils';

export default async function Page() {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);

  return <App appConfig={appConfig} />;
<<<<<<< HEAD
}
=======
}
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6
